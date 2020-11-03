from dataclasses import dataclass

from IPython.display import Javascript, display
from ipywidgets import HTML, Button, HBox, Layout

from ..utils import text_parser


def create_shortcuts_displays_helpers(shortcuts):
    """
    Create class names and tooltips for shortcuts to bind on.

    Parameters
    ----------
    shortcuts : List[Shortcut]
        List of shortcuts to create class names  and tooltips for.

    Returns
    -------
    shortcuts_class_names : Dict[str, Dict[str, str]]
        key : name of the shortcut
        value : class_name : name of the class to bind the shortcut on
                tooltip : string that represents the shortcut
    """
    shortcuts_class_names = {}
    for shortcut in shortcuts:
        shortcut_name_cleaned = shortcut.name.replace(" ", "_").lower()
        shortcuts_class_names[shortcut.name] = {
            "class_name": f"id_class_name_for_shortcut_{shortcut_name_cleaned}",
            "tooltip": shortcut.to_pretty_string(),
        }
    return shortcuts_class_names


@dataclass
class Shortcut:
    name: str
    key: str
    code: str
    shift_key: bool = False
    alt_key: bool = False
    ctrl_key: bool = False

    def to_js_shortcut(self, prefix="", class_name=""):
        """
        Convert shortcut to json containing the shortcut
        """
        js = {f"{prefix}class_name": class_name}
        for key in self.__dict__:
            value = self.__dict__[key]
            if type(value) == bool:
                value = "true" if value else "false"
            js[f"{prefix}{key}"] = value
        return js

    def to_pretty_string(self):
        pretty_string = ""
        if self.ctrl_key:
            pretty_string += "Ctrl + "

        if self.alt_key:
            pretty_string += "Alt + "

        if self.shift_key:
            pretty_string += "Shift + "

        pretty_string += f"{self.code} (Qwerty Keyboard)"
        return pretty_string


class ShortcutHelper:
    """
    Interface to help user select adequate shortcuts for the annotation.
    """

    def __init__(self):
        center_layout = Layout(
            display="flex", flex_flow="row", justify_content="center"
        )

        # Element to display the shortcut in
        html_shortcut = HTML(
            "<p id='shortcut-display'>Press the keyboard keys for the shortcut you want to use !</p>"  # noqa
        )

        # Element to hide the python version of the shortcut
        hidden_html_shortcut = HTML(
            """<p id="hidden-shortcut" style="display:none"></p>"""
        )

        # Display elements
        display(
            HBox(
                [html_shortcut, hidden_html_shortcut],
                layout=center_layout,
            )
        )

        # Display buttons
        stop_button = Button(description="Stop")
        stop_button.button_style = "danger"
        stop_button.add_class("stop_shortcut_button_class")

        copy_button = Button(description="Copy")
        copy_button.button_style = "info"
        copy_button.add_class("copy_shortcut_button_class")

        start_button = Button(description="Start")
        start_button.button_style = "success"
        start_button.add_class("start_shortcut_button_class")

        display(
            HBox(
                [stop_button, copy_button, start_button],
                layout=center_layout,
            )
        )

        # Start keyboard listeners and on click functions
        self.start_listener()

    def start_listener(self):
        display(
            Javascript(
                text_parser(
                    "shortcut_helper/shortcut_helper.js",
                )
            )
        )
