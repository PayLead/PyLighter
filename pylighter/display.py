import functools

from IPython.display import Javascript, clear_output, display
from ipywidgets import (HTML, BoundedIntText, Button, GridBox, HBox, Layout,
                        VBox)

from pylighter import config, utils

# -----------------------------------------------------------
# Main display
# -----------------------------------------------------------


def display_header(current_index, corpus_size, move_to_function, df_additional_infos):
    """
    Display the header of the annotation composed by the index of the current document
    (that can be changed via an input), the size of the corpus and additional
    information relative to the current document.
    """
    header_display = [instantiate_title(current_index, corpus_size, move_to_function)]

    if df_additional_infos is not None:
        header_display.append(
            instantiate_additional_infos(current_index, df_additional_infos)
        )

    vbox = VBox(header_display)
    vbox.add_class("card")
    vbox.add_class("card_header")
    display(vbox)


def instantiate_title(current_index, corpus_size, move_to_function):
    """
    Instantiate the ipywidgets elements that will be used to display the index of the
    current document (that can be changed via an input) and the size of the corpus.
    """
    title_layout = Layout(display="flex", flex_flow="row", justify_content="center")
    title_html = HTML("<h4>Document <b>n°</b></h4>")

    # Input to display the index of the current document
    document_number_input = BoundedIntText(
        value=current_index,
        min=0,
        max=corpus_size - 1,
        continuous_update=False,  # Only triggers the observer when unselected
    )
    document_number_input.add_class("document_number_input")

    # Add observer to the input area in order to move to any document
    document_number_input.observe(
        functools.partial(
            document_number_observer,
            current_index=current_index,
            move_function=move_to_function,
        ),
        "value",
    )
    corpus_size_html = HTML(f"<h4><b>/ {corpus_size-1}</b></h4>")

    return HBox(
        [title_html, document_number_input, corpus_size_html], layout=title_layout
    )


def document_number_observer(change, current_index, move_function):
    move_function(button=None, direction=(change.new - current_index))


def instantiate_additional_infos(current_index, df_additional_infos):
    """
    Instantiate the ipywidgets elements to display the additional information.
    """
    additional_infos = df_additional_infos.iloc[current_index]
    names = additional_infos.keys()

    subtitle_layout = Layout(
        display="flex", flex_flow="row wrap", justify_content="center"
    )
    subtitle_html = []

    for name in names:
        subtitle_html.append(HTML(f"{name}:&nbsp;<b>{str(additional_infos[name])}</b>"))

    return HBox(subtitle_html, layout=subtitle_layout)


def display_top_buttons(move_function, clear_function, shortcuts_displays_helpers={}):
    """
    Display the previous, next and skip buttons. Link them to any shortcuts if given.
    """
    # Create buttons
    previous_button = Button(
        description="Previous", button_style="info", icon="chevron-left"
    )
    previous_button.on_click(functools.partial(move_function, direction=-1))
    previous_button.add_class("move_button")

    clear_button = Button(description="Clear", button_style="danger", icon="undo")
    clear_button.on_click(functools.partial(clear_function))
    clear_button.add_class("move_button")

    skip_button = Button(description="Skip", button_style="warning", icon="forward")
    skip_button.on_click(functools.partial(move_function, direction=1, skip=True))
    skip_button.add_class("move_button")

    next_button = Button(description="Next", button_style="info", icon="chevron-right")
    next_button.on_click(functools.partial(move_function, direction=1))
    next_button.add_class("move_button")

    # Link shortcuts to the button
    previous_button = add_shortcut_to(
        previous_button, "previous", shortcuts_displays_helpers
    )
    clear_button = add_shortcut_to(clear_button, "clear", shortcuts_displays_helpers)
    skip_button = add_shortcut_to(skip_button, "skip", shortcuts_displays_helpers)
    next_button = add_shortcut_to(next_button, "next", shortcuts_displays_helpers)

    # Display buttons
    left = HBox([previous_button, clear_button])
    right = HBox([skip_button, next_button])
    hbox = HBox(
        [left, right],
        layout=Layout(display="flex", flex_flow="row", justify_content="space-between"),
    )
    hbox.add_class("move_buttons_margin")
    display(hbox)


def display_core(instantiated_core):
    display(instantiated_core)


def preload_core(obj, **kwargs):
    core_display, char_buttons, labels_buttons = instantiate_core(**kwargs)
    obj["core_display"] = core_display
    obj["char_buttons"] = char_buttons
    obj["labels_buttons"] = labels_buttons


def instantiate_core(
    document,
    char_params,
    char_on_click,
    labels_names,
    selected_labeliser,
    shortcuts_displays_helpers,
    label_on_click,
):
    """
    Instantiate the core elements (ie, the toolbox, the document and the chunk area).
    """

    document_display, char_buttons, labels_buttons = instantiate_document(
        document,
        char_params,
        char_on_click,
        labels_names,
        selected_labeliser,
        shortcuts_displays_helpers,
        label_on_click,
    )
    chunks_area_display = instantiate_chunks_area(labels_names)

    core_display = GridBox(
        children=[document_display, chunks_area_display],
        layout=Layout(
            width="100%",
            grid_template_columns="60% 40%",
        ),
    )

    return core_display, char_buttons, labels_buttons


def instantiate_toolbox(
    labels_names, selected_labeliser, shortcuts_displays_helpers, label_on_click
):
    """
    Instantiate the toolbox containing the buttons of the different labels and the eraser.
    """
    # Instantiate labels buttons
    labels_buttons = []
    for index, label in enumerate(labels_names):
        button = Button(description=label)
        if label == selected_labeliser:
            button.add_class(f"{label}_color_selected")
        else:
            button.add_class(f"{label}_color")
        button.on_click(functools.partial(label_on_click, button_index=index))
        button.add_class("label_button")
        button = add_shortcut_to(button, label, shortcuts_displays_helpers)
        labels_buttons.append(button)

    # Instantiate eraser
    eraser_button = Button(icon="eraser", layout=Layout(width="40px"))
    eraser_button.on_click(
        functools.partial(label_on_click, button_index=len(labels_names))
    )
    eraser_button.add_class("label_button")
    eraser_button.add_class("eraser_color")
    eraser_button = add_shortcut_to(eraser_button, "eraser", shortcuts_displays_helpers)

    labels_buttons.append(eraser_button)

    labels_display = HBox(
        labels_buttons,
        layout=Layout(display="flex", flex_flow="row wrap", justify_content="center"),
    )

    return labels_display, labels_buttons


def instantiate_document(
    document,
    char_params,
    char_on_click,
    labels_names,
    selected_labeliser,
    shortcuts_displays_helpers,
    label_on_click,
):
    """
    Instantiate the document display.
    A document composed of n chars is displayed as n buttons.
    """
    buttons = [None] * len(document)
    buttons_display = []
    current_word = []

    char_layout = Layout(min_width=char_params["min_width_between_chars"])
    space_layout = Layout(min_width=char_params["width_white_space"])

    # Create the correct button associated to each char
    for char_index, char in enumerate(document):
        # Create buton
        button_layout = char_layout
        if char == " ":
            button_layout = space_layout
        button = Button(description=char, layout=button_layout)

        button.style.button_color = "transparent"
        button.add_class("char_display")
        button.on_click(functools.partial(char_on_click, char_index=char_index))

        # Differentiate chars from spaces to have a good word wrap
        if char == " ":
            current_word.append(button)
            buttons_display.append(HBox(current_word))
            current_word = []
        else:
            current_word.append(button)
        buttons[char_index] = button

    if current_word:
        buttons_display.append(HBox(current_word))

    # Create the global display
    toolbox_display, labels_buttons = instantiate_toolbox(
        labels_names, selected_labeliser, shortcuts_displays_helpers, label_on_click
    )
    divider = HTML("<hr style='margin-top:0.5em;margin-bottom:0.5em'>")
    hbox = HBox(
        buttons_display,
        layout=Layout(
            display="flex",
            flex_flow="row wrap",
        ),
    )
    document_display = VBox(
        [toolbox_display, divider, hbox],
    )
    document_display.add_class("card")

    return document_display, buttons, labels_buttons


def instantiate_chunks_area(labels_names):
    """
    Instantiate the ipywidgets elements that will be used to display chunks.
    """
    chunks_box = HBox(
        [],
        layout=Layout(
            display="flex",
            flex_flow="row wrap",
            height="fit-content",
            width="1OO%",
        ),
    )
    chunks_box.add_class("id_class_hbox_label")
    chunk_area_display = HBox(
        [chunks_box],
        layout=Layout(
            width="1OO%",
            height="auto",
        ),
    )
    chunk_area_display.add_class("card")

    return chunk_area_display


def display_chunk(chunk, chunk_text, delete_chunk_on_click):
    """
    Display the given chunk with the given text in the chunk area (next to the last one).
    """
    # Create HTML equivalent of the chunk text
    text = HTML(utils.chunk_html_display(chunk_text), layout=Layout(height="10px"))
    text.add_class("chunk_text_size")
    text.add_class(f"{chunk.label}_color")
    chunk.text_display = text

    # Create the delete button to delete the chunk
    delete_button = Button(
        icon="times",
    )
    delete_button.add_class("delete_chunk_button")
    delete_button.on_click(functools.partial(delete_chunk_on_click, chunk=chunk))

    # Create the display of the chunk
    chunk_display = HBox(
        [text, delete_button],
        layout=Layout(margin="2px 5px 2px 5px", padding="5px 5px 5px 5px"),
    )
    chunk_display.add_class(f"{chunk.label}_color")
    chunk_display.add_class("chunk_tag")

    # Add class id to recognize it
    chunk_display.add_class(chunk.display_id)

    # Display chunk_display then move it to the correct spot
    chunk_display.add_class("invisible")
    display(chunk_display)
    display(Javascript(utils.js_add_el_to_div(chunk.display_id, "id_class_hbox_label")))
    chunk_display.remove_class("invisible")


def display_additional_outputs(additional_outputs_elements, additional_outputs_values):
    hbox_elements = ["checkbox"]

    # Create elements
    elements_to_display = []
    input_elements = []
    for element in additional_outputs_elements:
        value = element.default_value
        if additional_outputs_values.notna()[element.name]:
            value = additional_outputs_values[element.name]

        description_element = HTML(
            f"<b style='font-size:1.1em'>{element.description}</b>",
            layout=Layout(margin="auto 0px auto 0px"),
        )
        input_element = config.DISPLAY_ELEMENTS[element.display_type](value=value)
        if element.display_type in hbox_elements:
            # Remove indentation
            input_element.indent = False
            display_element = HBox([input_element, description_element])
        else:
            display_element = VBox([description_element, input_element])

        elements_to_display.append(display_element)
        input_elements.append(input_element)

    additional_outputs_area = GridBox(
        elements_to_display,
        layout=Layout(
            # width="auto",
            grid_template_columns="50% 50%",
            grid_template_rows="auto",
            grid_gap="1em 1em",
        ),
    )
    additional_outputs_area.add_class("card")
    display(additional_outputs_area)
    return input_elements


def display_footer(save_function, quit_function, shortcuts_displays_helpers):
    """
    Display the footer of the annotation. It is composed of the quit and the save buttons.
    """
    # Create buttons
    quit_button = Button(description="Quit", button_style="danger", icon="sign-out")
    quit_button.on_click(quit_function)
    quit_button.add_class("footer_button")

    save_button = Button(description="Save", button_style="success", icon="save")
    save_button.on_click(save_function)
    save_button.add_class("footer_button")

    # Link shortcuts to the button
    quit_button = add_shortcut_to(quit_button, "quit", shortcuts_displays_helpers)
    save_button = add_shortcut_to(save_button, "save", shortcuts_displays_helpers)

    # Display buttons
    hbox = HBox(
        [quit_button, save_button],
        layout=Layout(display="flex", flex_flow="row", justify_content="space-between"),
    )
    hbox.add_class("footer_margin")
    display(hbox)


def display_quit_text(current_index, corpus_size, start_index):
    display(
        HTML(
            f"""Good job, you annotated <b>{abs(current_index - start_index)}</b>
            documents ! Keep up the good work !"""
        )
    )

    if corpus_size != current_index:
        display(
            HTML(
                f"""<p>If you want to continue where you left, make sure to keep the
                    index of the last document:
                    <h4 style='color:#f44336'><b>{current_index}</b></h4><p>"""
            ),
        )


def clear_display():
    clear_output(wait=True)


# -----------------------------------------------------------
# Utils display
# -----------------------------------------------------------


def highlight_chars(char_buttons, selected_labeliser, labels_names, undo):
    for char_button in char_buttons:
        # For overlap, remove all previous color
        for label in labels_names:
            if label != selected_labeliser:
                char_button.remove_class(f"{label}_color")

        # Add the appropriate color the char
        if not undo:
            char_button.add_class(f"{selected_labeliser}_color")
        else:
            char_button.remove_class(f"{selected_labeliser}_color")


def remove_chunk(chunk):
    if chunk.display_id:
        display(Javascript(utils.js_remove_el(chunk.display_id)))


def update_chunk_text(new_text, chunk, delete_chunk_on_click):
    if chunk.text_display:
        chunk.text_display.value = utils.chunk_html_display(new_text)
    else:
        display_chunk(chunk, new_text, delete_chunk_on_click)


def add_shortcut_to(button, name, shortcuts_displays_helpers):
    shortcut_display_helper = shortcuts_displays_helpers.get(name)
    if shortcut_display_helper:
        button.add_class(shortcut_display_helper["class_name"])
        button.tooltip = shortcut_display_helper["tooltip"]
    return button


def prepare_toast():
    # Remove toast if already exists
    display(
        Javascript(
            """let snackbar = document.getElementById('snackbar')
                if (snackbar) {
                    snackbar.remove()
                }"""
        )
    )

    # Load css and html
    css = utils.text_parser("toast/toast.css")
    html = utils.text_parser(
        "toast/toast.html",
    )

    # Display css and HTML
    display(HTML(f"<style>{css}</style>{html}"))

    # Append element to body so that the toast is on top
    display(
        Javascript("document.body.appendChild(document.getElementById('snackbar'))")
    )


def show_toast(msg, success):
    js = utils.text_parser(
        "toast/toast.js",
        success_type="success" if success else "error",
        toast_msg=msg,
    )
    display(Javascript(js))


def define_custom_styles(labels_colors, char_params):
    # Define colors for labels
    css_colors = ""
    for label_color in labels_colors:
        selected_label_color = utils.compute_selected_label_color(
            label_color.background_color
        )
        css_colors += utils.text_parser(
            "css/color.css",
            background_color_selected=selected_label_color,
            text_color_selected=label_color.text_color,
            **label_color.__dict__,
        )

    # Define color for eraser
    css_colors += utils.text_parser(
        "css/color.css",
        name="eraser",
        text_color="white",
        text_color_selected="white",
        background_color_selected=config.ERASER_COLOR,
        background_color=config.ERASER_COLOR,
    )

    # Define global style
    css_styles = utils.text_parser(
        "css/style.css",
        char_font_size=char_params["font_size"],
        colors=css_colors,
    )
    display(HTML(f"<style>{css_styles}</style>"))


def define_keyboard_shortcuts(shortcuts, shortcuts_class_names):
    # [Hack] Define shortcut to remove keyboard listener
    cancel_shortcuts = config.SHORTCUT_CANCEL_SHORTCUTS.to_js_shortcut(
        prefix="cancel_shortcuts_",
    )

    # Define custom shortcuts
    custom_key_shortcuts = ""
    for shortcut in shortcuts:
        custom_key_shortcuts += utils.text_parser(
            "js/key_shortcut.js",
            **shortcut.to_js_shortcut(
                class_name=shortcuts_class_names[shortcut.name]["class_name"]
            ),
        )
    js_keyboard_listeners = utils.text_parser(
        "js/key_shortcuts.js",
        custom_key_shortcuts=custom_key_shortcuts,
        **cancel_shortcuts,
    )

    display(Javascript(js_keyboard_listeners))


def display_loader():
    loader = HTML(utils.text_parser("loader.html"))
    display(loader)
    return loader


def remove_loader(loader):
    loader.close()
