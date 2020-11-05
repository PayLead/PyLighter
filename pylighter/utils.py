import colorsys
import pkgutil
from dataclasses import dataclass

import pandas as pd

from pylighter import config


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


def assert_IOB2_format(labels_list):
    for labels in labels_list:
        previous_label = None
        for label in labels:
            assert label == "O" or label[:2] == "B-" or label[:2] == "I-"

            if label == "O":
                previous_label = None
                continue

            if label[:2] == "B-":
                previous_label = label[2:]

            else:
                assert previous_label
                assert previous_label == label[2:]


def assert_input_consistency(corpus, labels, start_index):
    if labels:
        assert len(corpus) == len(labels)
        assert_IOB2_format(labels)

    assert start_index >= 0
    assert start_index < len(corpus)


def compute_selected_label_color(str_color_hex):
    rgb = tuple(
        int(str_color_hex.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4)  # noqa
    )
    hue, lightness, saturation = colorsys.rgb_to_hls(*rgb)
    lightness *= 0.8
    return f"hsl({int(hue*360)}, {int(saturation * 100)}%, {int(lightness * 100)}%)"


def wait_for_threads(threads):
    for thread in threads:
        thread.join()
    threads = []


@dataclass
class LabelColor:
    name: str
    text_color: str
    background_color: str


class AdditionalOutputElement:
    def __init__(self, name, display_type, description, default_value):
        self.name = name
        self.display_type = display_type
        self.description = description
        self.default_value = default_value

        if display_type not in config.DISPLAY_ELEMENTS.keys():
            raise ValueError(
                f"display_type must one of those {config.DISPLAY_ELEMENTS.keys()}"
            )


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
