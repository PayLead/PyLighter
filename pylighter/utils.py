import colorsys
import pkgutil
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


def text_parser(file_name, **kwargs):
    """Parse text and replace <% variable %> by the value of variable.

    Parameters
    ----------
    file_name : str
        Path to the file

    Returns
    -------
    file_content : str
        The content of the file
    """

    file_content = str(pkgutil.get_data("pylighter", file_name), "utf-8")
    file_content = file_content.replace("\n", "")

    for key in kwargs:
        file_content = file_content.replace(f"<% {key} %>", kwargs[key])

    return file_content


def js_add_el_to_div(class_name_source, class_name_target):
    """
    Js function to append source element to the target one.
    """
    js = f"document.getElementsByClassName('{class_name_target}')[0]"
    js += f".appendChild(document.getElementsByClassName('{class_name_source}')[0])"
    return js


def js_remove_el(el_id_class_name):
    return f"document.getElementsByClassName('{el_id_class_name}')[0].remove()"


def chunk_html_display(text):
    if text and text[-1] == " ":
        text = text[:-1] + "␣"
    return f"{text}"


def annotation_to_csv(corpus, labels, additional_outputs_values, file_path):
    df = pd.DataFrame(data={"document": corpus, "labels": labels})
    if additional_outputs_values is not None:
        df = pd.concat([df, additional_outputs_values], axis=1)
    df.to_csv(file_path, sep=";", index=False)


def assert_input_consistency(corpus, labels, start_index):
    if labels:
        assert len(corpus) == len(labels)

    assert start_index >= 0
    assert start_index < len(corpus)


def compute_selected_label_color(str_color_hex):
    rgb = tuple(int(str_color_hex.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(*rgb)
    l *= 0.8
    return f"hsl({int(h*360)}, {int(s*100)}%, {int(l*100)}%)"


def wait_for_threads(threads):
    for thread in threads:
        thread.join()
    threads = []


@dataclass
class LabelColor:
    name: str
    text_color: str
    background_color: str


class AdditionnalOutputElement:
    def __init__(self, name, display_type, description, default_value):
        self.name = name
        self.display_type = display_type
        self.description = description
        self.default_value = default_value


class PreloadedDisplays:
    def __init__(
        self,
    ):
        self.previous = {}
        self.current = {}
        self.next = {}

    def update(self, direction):
        if direction == 1:
            self.previous = self.current
            self.current = self.next
            self.next = {}
        elif direction == -1:
            self.next = self.current
            self.current = self.previous
            self.previous = {}
        else:
            self.next = {}
            self.current = {}
            self.previous = {}
