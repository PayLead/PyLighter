import ast
from datetime import datetime

import pandas as pd
import pytest

from pylighter import Annotation


@pytest.mark.parametrize(
    "labels, expected",
    [
        ([["O", "O", "O", "O"]], [["O", "O", "O", "O"]]),
        ([["O", "B-1", "I-1", "I-1"]], [["O", "B-1", "I-1", "I-1"]]),
        (None, [["O", "O", "O", "O"]]),
    ],
)
def test_init_labels(labels, expected):
    sentences = ["This"]
    annotation = Annotation(sentences, labels=labels)
    assert annotation.labels == expected


def test_select_new_labeliser():
    sentences = ["This is a sentence"]
    annotation = Annotation(sentences)

    assert annotation.selected_labeliser == annotation.labels_names[0]

    annotation._select_new_labeliser(button=None, button_index=1)
    assert annotation.selected_labeliser == annotation.labels_names[1]


@pytest.mark.parametrize(
    "labels, start_index, char_index, expected",
    [
        (["O", "O", "O", "O"], None, 2, ["O", "O", "B-1", "O"]),
        (["O", "O", "O", "O"], 0, 2, ["B-1", "I-1", "I-1", "O"]),
        (["O", "O", "O", "O"], 2, 0, ["B-1", "I-1", "I-1", "O"]),
        (["B-2", "I-2", "O", "O"], None, 2, ["B-2", "I-2", "B-1", "O"]),
        (["B-2", "I-2", "O", "O"], 2, 3, ["B-2", "I-2", "B-1", "I-1"]),
        (["B-2", "I-2", "O", "O"], None, 0, ["B-1", "B-2", "O", "O"]),
        (["B-2", "I-2", "O", "O"], 0, 1, ["B-1", "I-1", "O", "O"]),
        (["B-2", "I-2", "O", "O"], 0, 2, ["B-1", "I-1", "I-1", "O"]),
        (["B-2", "I-2", "O", "O"], 2, 0, ["B-1", "I-1", "I-1", "O"]),
        (["B-2", "I-2", "O", "O"], 0, 0, ["B-1", "B-2", "O", "O"]),
    ],
)
def test_labelise(labels, start_index, char_index, expected):
    labels_names = ["1", "2", "3"]

    sentences = ["This is a sentence"]
    annotation = Annotation(sentences, labels=[labels], labels_names=labels_names)

    assert annotation.chunks.to_labels() == annotation.labels[0]

    annotation.label_start_index = start_index
    annotation._labelise(
        button=None,
        char_index=char_index,
    )

    assert annotation.chunks.to_labels() == expected


@pytest.mark.parametrize(
    "labels, start_index, char_index, expected",
    [
        (["O", "O", "O", "O"], None, 2, ["O", "O", "O", "O"]),
        (["O", "O", "O", "O"], 0, 2, ["O", "O", "O", "O"]),
        (["O", "O", "O", "O"], 2, 0, ["O", "O", "O", "O"]),
        (["B-2", "I-2", "O", "O"], None, 2, ["B-2", "I-2", "O", "O"]),
        (["B-2", "I-2", "O", "O"], 2, 3, ["B-2", "I-2", "O", "O"]),
        (["B-2", "I-2", "O", "O"], None, 0, ["O", "B-2", "O", "O"]),
        (["B-2", "I-2", "O", "O"], 0, 1, ["O", "O", "O", "O"]),
        (["B-2", "I-2", "O", "O"], 0, 2, ["O", "O", "O", "O"]),
        (["B-2", "I-2", "O", "O"], 2, 0, ["O", "O", "O", "O"]),
        (["B-2", "I-2", "O", "O"], 0, 0, ["O", "B-2", "O", "O"]),
    ],
)
def test_eraser(labels, start_index, char_index, expected):
    labels_names = ["1", "2", "3"]

    sentences = ["This is a sentence"]
    annotation = Annotation(sentences, labels=[labels], labels_names=labels_names)

    assert annotation.chunks.to_labels() == annotation.labels[0]

    annotation.label_start_index = start_index
    annotation.selected_labeliser = None
    annotation._labelise(
        button=None,
        char_index=char_index,
    )

    assert annotation.chunks.to_labels() == expected


@pytest.mark.parametrize(
    "start_index, direction, expected",
    [
        (0, 1, 1),
        (1, -1, 0),
        (0, -1, 0),
        (3, 1, 4),
    ],
)
def test_change_sentence(start_index, direction, expected):
    sentences = ["Sentence 1", "Sentence 2", "Sentence 3", "Sentence 4"]
    annotation = Annotation(sentences, start_index=start_index, save_path="/dev/null")

    assert annotation.current_index == start_index

    annotation._change_sentence(button=None, direction=direction)
    assert annotation.current_index == expected


@pytest.mark.parametrize(
    "sentences, labels",
    [
        (
            ["Test", "Save", "!"],
            [["B-1", "I-1", " I-1", " I-1"], ["O", "B-1", "I-1", "I-1"], ["O"]],
        ),
        (
            ["Test", "Save", "!"],
            None,
        ),
    ],
)
def test_save(sentences, labels):
    save_path = "/tmp/" + str(datetime.now()).replace(" ", "_")
    annotation = Annotation(
        sentences,
        labels=labels,
        save_path=save_path,
    )

    if not labels:
        labels = annotation.labels

    annotation._save()

    df = pd.read_csv(save_path, sep=";")

    assert "sentences" in df.columns
    assert "labels" in df.columns

    assert df.sentences.to_list() == sentences
    assert df.labels.apply(ast.literal_eval).to_list() == labels
