import os
import threading

import pandas as pd

from pylighter import config
from pylighter import display as display_helper
from pylighter import utils
from pylighter.chunk_models import Chunk, Chunks
from pylighter.shortcut_helper import shortcut_helper


class Annotation:
    """
    Class used to annotate datasets.
    """

    # --------------------------------------------
    # Initialization
    # --------------------------------------------

    def __init__(
        self,
        corpus,
        labels=None,
        start_index=0,
        save_path=config.ANNOTATION_SAVE_PATH,
        labels_names=config.LABELS_NAMES,
        labels_colors=config.DEFAULT_COLORS,
        additional_infos=None,
        additional_outputs_values=None,
        additional_outputs_elements=None,
        standard_shortcuts=config.SHORTCUTS,
        labels_shortcuts=None,
        char_params=config.CHAR_PARAMS,
    ):
        """
        Class that starts the user interface to annotate the given corpus.

        Parameters
        ----------
        corpus : List[str]
             The corpus to annotate.
        labels : List[List[str]], optional
            The labels of the documents. It must have the same length as documents.
            Moreover, the i-th label must have the same length as the number of
            characters of the i-th document.
            By default, none of the documents are annotated.
        start_index : int, optional
            The index of the document to start on. Default value is 0.
        save_path : str, optional
            Path to store the annotated corpus into a csv when clicking the save button.
            By default, the (document, labels) are stored in config.ANNOTATION_SAVE_PATH.
        labels_names : List[str], optional
            The names of your labels. Default value is config.LABELS_NAMES.
        labels_colors : List[str], optional
            The colors for your labels in hex format (ex: "#2DA9D5").
            The first label in labels_names will have the first color in labels_colors.
            By default, the labels colors are defined in config.DEFAULT_COLORS.
        labels_shortcuts : List[Shortcut], optional
            Keyboard shortcuts to use to select a given label. A shortcut is linked to
            one of the label button only if they share the same name.
            By default, none of the labels buttons have keyboard shortcuts.
        additional_infos : pd.DataFrame, optional
            Dataframe of size (size of the corpus, n) containing additional infos to
            display for each document. By default, no additional infos are displayed.
        additional_outputs_elements : List[AdditionalOutputElement], optional
            List containing additional elements to display. 5 elements type are supported:
            checkbox, int_text, float_text, text, text_area. By default, there won't be
            any additional outputs.
        additional_outputs_values : pandas.DataFrame, optional
            DataFrame of size (size of the corpus, n) containing the values of additional
            outputs for each document. If additional_outputs_elements are given, then the
            columns of this DataFrame must match the names of the elements given.
            By default, it will be initialized with default values given by the
            additional_outputs_elements if it exists.
        shortcuts : List[Shortcut], optional
            Keyboard shortcuts for the different buttons (Next, Previous, Skip and Save).
            By default, it uses the keyboard shortcuts defined in config.SHORTCUTS
        char_params : Dict[str, str], optional
            Parameters to modify the display of the characters in the document.
            The correct values are:
                min_width_between_chars -- Min distance between two chars. Expects a css
                                            value as string (ex: "4px").
                width_white_space -- Size of a white space. Expects a css value as
                                            string (ex: "10px").
                font_size -- Size of the font. Expects a css value as string (ex:"large").
        """
        # Check input consistency
        utils.assert_input_consistency(corpus, labels, start_index)

        # Init "global" variables
        self.start_index = start_index
        self.current_index = start_index
        self.corpus = corpus
        self.labels = self._init_labels(labels)
        self.save_path = save_path
        self.char_params = char_params
        self.additional_infos = additional_infos
        self._init_additional_outputs(
            additional_outputs_values, additional_outputs_elements
        )
        self.labels_names = labels_names
        self.labels_colors = self._init_labels_colors(labels_colors)
        self.threads = []

        display_helper.start_display()

        all_shortcuts = standard_shortcuts[:]
        if labels_shortcuts:
            all_shortcuts += labels_shortcuts
        self.shortcuts_displays_helpers = (
            shortcut_helper.create_shortcuts_displays_helpers(all_shortcuts)
        )
        display_helper.define_keyboard_shortcuts(
            all_shortcuts, self.shortcuts_displays_helpers
        )

        self.preloaded_displays = utils.PreloadedDisplays()

        # Start annotating
        self._annotate()

    def _init_labels(self, labels):
        """
        Init labels as "empty" if not labels are given
        """
        if not labels:
            labels = []
            for document in self.corpus:
                labels.append(["O"] * len(document))

        return labels

    def _init_additional_outputs(
        self, additional_outputs_values, additional_outputs_elements
    ):
        self.additional_outputs_elements = additional_outputs_elements
        if (
            additional_outputs_elements is not None
            and additional_outputs_values is None
        ):
            # Create empty dataframe if none is given
            columns = [element.name for element in additional_outputs_elements]
            self.additional_outputs_values = pd.DataFrame(
                columns=columns, index=range(len(self.corpus))
            )
        else:
            # Use given data
            self.additional_outputs_values = additional_outputs_values

    def _init_labels_colors(self, labels_colors_hex):
        labels_colors = []
        for index, label_name in enumerate(self.labels_names):
            labels_colors.append(
                utils.LabelColor(
                    name=label_name,
                    text_color="white",
                    background_color=labels_colors_hex[index % len(labels_colors_hex)],
                )
            )
        return labels_colors

    # --------------------------------------------
    # Main
    # --------------------------------------------

    def _annotate(self):
        """
        Method to annotate the current document. It is responsible for setting up the
        user interface and the variables needed on buttons clicked.
        """

        # Init variables specific to the current document
        self.document = self.corpus[self.current_index]
        self.chunks = Chunks(labels=self.labels[self.current_index])
        self.selected_labeliser = self.labels_names[0]
        self.label_start_index = None
        self.additional_outputs_elements_displays = None

        # Display loader until the display is finished
        loader = display_helper.display_loader()

        # Load current core if not preloaded
        self._async_load(self.preloaded_displays.current, 0)

        # Define custom styles
        display_helper.define_custom_styles(self.labels_colors, self.char_params)

        # Display header
        display_helper.display_header(
            self.current_index,
            len(self.corpus),
            self._change_document,
            self.additional_infos,
        )

        # Display moving buttons
        display_helper.display_top_buttons(
            self._change_document,
            self._clear_current,
            self.shortcuts_displays_helpers,
        )

        # Display document, toolbox and chunk area
        utils.wait_for_threads(self.threads)
        display_helper.display_core(self.preloaded_displays.current["core_display"])
        self.char_buttons = self.preloaded_displays.current["char_buttons"]
        self.labels_buttons = self.preloaded_displays.current["labels_buttons"]

        # Display current chunks
        for chunk in self.chunks.chunks:
            self._sync_chunks(
                chunk, self.document[chunk.start_index : chunk.end_index + 1]  # noqa
            )

        if self.additional_outputs_elements:
            self.additional_outputs_elements_displays = (
                display_helper.display_additional_outputs(
                    self.additional_outputs_elements,
                    self.additional_outputs_values.iloc[self.current_index],
                )
            )

        # Display footer
        display_helper.display_footer(
            self._save,
            self._quit,
            self.shortcuts_displays_helpers,
        )

        # Remove loader
        display_helper.remove_loader(loader)

        # Prepare toast for on_save
        display_helper.prepare_toast()

        # Preload missing displays
        self._async_load(self.preloaded_displays.next, 1)
        self._async_load(self.preloaded_displays.previous, -1)

    def _async_load(self, preloaded, direction):
        """
        Compute the core display (ie toolbox, document and chunk area) and stores it in
        the preloaded object if not already precomputed. The displays are computed in
        other threads, so make sure to join the threads before accessing/updating any
        value in the preloaded object.


        Parameters
        ----------
        preloaded : Dict[str, ...]
            Object for storing the values returned by the display if the dict is empty.
            Values are:
            - core_display {ipywidgets.Box}: The widget that represents the core display.
            - char_buttons {List[ipywidgets.Button]}: The buttons for every char.
            - labels_buttons {List[ipywidgets.Button]}: The buttons for every label.
        direction : int
            Represents the direction (and the distance) to the next document.
            For instance, if the direction equals 2 then it preloads the document at
            current index + 2.
        """
        if (
            not preloaded
            and self.current_index + direction < len(self.corpus)
            and self.current_index + direction >= 0
        ):
            thread = threading.Thread(
                target=display_helper.preload_core,
                kwargs={
                    "obj": preloaded,
                    "document": self.corpus[self.current_index + direction],
                    "char_params": self.char_params,
                    "char_on_click": self._labelise,
                    "labels_names": self.labels_names,
                    "selected_labeliser": self.labels_names[0],
                    "shortcuts_displays_helpers": self.shortcuts_displays_helpers,
                    "label_on_click": self._select_new_labeliser,
                },
            )
            thread.start()
            self.threads.append(thread)

    # --------------------------------------------
    # On click functions
    # --------------------------------------------

    def _select_new_labeliser(self, button, button_index):
        # Remove selected class from all buttons
        for labeliser_button in self.labels_buttons:
            labeliser_button.remove_class(
                f"{labeliser_button.description or labeliser_button.icon}_color_selected"
            )
            labeliser_button.add_class(
                f"{labeliser_button.description or labeliser_button.icon}_color"
            )

        # Add selected class to the current selected labeliser
        description = (
            self.labels_buttons[button_index].description
            or self.labels_buttons[button_index].icon
        )
        self.labels_buttons[button_index].add_class(f"{description}_color_selected")
        self.selected_labeliser = self.labels_buttons[button_index].description
        if button_index == len(self.labels_buttons) - 1:
            # Selects the eraser
            self.selected_labeliser = None

        # Restart the index to none
        self.label_start_index = None

    def _labelise(self, button, char_index):
        # Selecting the first part and create chunks accordingly
        if self.label_start_index is None:
            chunk = Chunk(
                start_index=char_index,
                end_index=char_index,
                label=self.selected_labeliser,
            )
            self.label_start_index = char_index

        # Selecting the second part and create chunks accordingly
        else:
            start_index = self.label_start_index
            end_index = char_index
            if end_index < start_index:
                start_index, end_index = end_index, start_index

            chunk = Chunk(
                start_index=start_index,
                end_index=end_index,
                label=self.selected_labeliser,
            )
            self.label_start_index = None

        # Update chunks with the new chunk
        chunk_text = self.document[chunk.start_index : chunk.end_index + 1]  # noqa
        updated_chunks, removed_chunks = self.chunks.add_new_chunk_and_update(chunk)

        # Remove the freshly created chunk if the eraser is selected
        display_new_chunk = True
        if self.selected_labeliser is None:
            self.chunks.remove_chunk_by_id(chunk.id)
            display_new_chunk = False
            chunk.display_id = None

        # Sync the display with the chunks
        self._sync_chunks(
            chunk, chunk_text, updated_chunks, removed_chunks, display_new_chunk
        )

    def _sync_chunks(
        self,
        chunk,
        chunk_text,
        updated_chunks=[],
        removed_chunks=[],
        display_chunk=True,
    ):
        """
        Sync the given chunk display with the current state of the chunks.
        """
        # Display new char highlight
        display_helper.highlight_chars(
            char_buttons=self.char_buttons[
                chunk.start_index : chunk.end_index + 1  # noqa
            ],
            selected_labeliser=chunk.label,
            labels_names=self.labels_names,
            undo=False,
        )

        # Remove chunks from display
        for chunk_removed in removed_chunks:
            display_helper.remove_chunk(chunk_removed)

        # Update chunks text
        for chunk_updated in updated_chunks:
            display_helper.update_chunk_text(
                self.document[
                    chunk_updated.start_index : chunk_updated.end_index + 1  # noqa
                ],
                chunk_updated,
                delete_chunk_on_click=self._delete_chunk,
            )

        # Display new chunk
        if display_chunk:
            display_helper.display_chunk(
                chunk,
                chunk_text,
                self._delete_chunk,
            )

    def _delete_chunk(self, button, chunk):
        # Remove chunk from chunks
        self.chunks.remove_chunk_by_id(chunk.id)

        # Remove chunk
        display_helper.remove_chunk(chunk)

        # Remove char chunk highlight
        display_helper.highlight_chars(
            char_buttons=self.char_buttons[
                chunk.start_index : chunk.end_index + 1  # noqa
            ],
            selected_labeliser=chunk.label,
            labels_names=self.labels_names,
            undo=True,
        )

    def _change_document(self, button, direction, skip=False):
        """
        Go from the current document at index i to the document at index i + direction.
        If skip is True, the current annotation is not added to the labels.
        """
        # Add current annotation to the labels if skip is False
        if not skip:
            self.labels[self.current_index] = self.chunks.to_labels()

            # Update additional outputs values
            if self.additional_outputs_elements:
                for index, element in enumerate(self.additional_outputs_elements):
                    self.additional_outputs_values.iloc[self.current_index][
                        element.name
                    ] = self.additional_outputs_elements_displays[index].value

        if self.current_index + direction < 0:
            return

        # Move to the next document
        self.current_index += direction

        # Clear the current display
        display_helper.clear_display()

        if self.current_index >= len(self.corpus):
            # All done
            self._save()
            self._quit()
        else:
            # Continue annotation
            utils.wait_for_threads(self.threads)
            self.preloaded_displays.update(direction)
            self._annotate()

    def _clear_current(self, button):
        # Clearing the current document <=> Using the eraser on the whole document.
        current_labeliser = self.selected_labeliser
        self.selected_labeliser = None
        self.label_start_index = 0
        self._labelise(None, len(self.document) - 1)
        self.selected_labeliser = current_labeliser

    def _save(self, button=None, file_path=None):
        """
        Saves the current state of the corpus and the labels into a csv.
        """
        try:
            # Save file in path
            if not file_path:
                file_path = self.save_path
            file_path = os.path.abspath(file_path)
            utils.annotation_to_csv(
                self.corpus, self.labels, self.additional_outputs_values, file_path
            )

            # Display success toast
            display_helper.show_toast(
                msg=f"File successfully saved in <b>{file_path}</b> !", success=True
            )
        except Exception as err:
            # Display error toast with error message
            display_helper.show_toast(msg=str(err), success=False)

    def _quit(self, button=None):
        # Display end screen
        display_helper.clear_display()
        display_helper.display_quit_text(
            self.current_index, len(self.corpus), self.start_index
        )
