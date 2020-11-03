import ast
from datetime import datetime

import pandas as pd
import pytest

from pylighter import AdditionalOutputElement, Annotation


@pytest.mark.parametrize(
    "labels, expected",
    [
        ([["O", "O", "O", "O"]], [["O", "O", "O", "O"]]),
        ([["O", "B-1", "I-1", "I-1"]], [["O", "B-1", "I-1", "I-1"]]),
        (None, [["O", "O", "O", "O"]]),
    ],
)
def test_init_labels(labels, expected):
    corpus = ["This"]
    annotation = Annotation(corpus, labels=labels)
    assert annotation.labels == expected


def test_select_new_labeliser():
    corpus = ["This is a sentence"]
    annotation = Annotation(corpus)

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

    corpus = ["This is a sentence"]
    annotation = Annotation(corpus, labels=[labels], labels_names=labels_names)

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

    corpus = ["This is a sentence"]
    annotation = Annotation(corpus, labels=[labels], labels_names=labels_names)

    assert annotation.chunks.to_labels() == annotation.labels[0]

    annotation.label_start_index = start_index
    annotation.selected_labeliser = None
    annotation._labelise(
        button=None,
        char_index=char_index,
    )

    assert annotation.chunks.to_labels() == expected


@pytest.mark.parametrize(
    "start_index, direction, skip, expected",
    [
        (0, 1, False, 1),
        (1, -1, False, 0),
        (0, -1, False, 0),
        (3, 1, False, 4),
        (0, 3, False, 3),
        (2, -2, False, 0),
        (0, 1, True, 1),
        (1, -1, True, 0),
        (0, -1, True, 0),
        (3, 1, True, 4),
        (0, 3, True, 3),
        (2, -2, True, 0),
    ],
)
def test_change_document(start_index, direction, skip, expected):
    corpus = ["Sentence 1", "Sentence 2", "Sentence 3", "Sentence 4"]
    labels_names = ["1", "2", "3"]
    annotation = Annotation(
        corpus,
        start_index=start_index,
        labels_names=labels_names,
        save_path="/dev/null",
    )

    assert annotation.current_index == start_index

    # Labelise word "sentence"
    annotation.label_start_index = 0
    annotation._labelise(
        button=None,
        char_index=7,
    )
    expected_labels = ["B-1", "I-1", "I-1", "I-1", "I-1", "I-1", "I-1", "I-1", "O", "O"]

    annotation._change_document(button=None, direction=direction, skip=skip)
    assert annotation.current_index == expected

    if skip:
        expected_labels = ["O"] * len(corpus[0])
    assert annotation.labels[start_index] == expected_labels


@pytest.mark.parametrize(
    "corpus, labels",
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
def test_save(corpus, labels):
    save_path = "/tmp/" + str(datetime.now()).replace(" ", "_")
    annotation = Annotation(
        corpus,
        labels=labels,
        save_path=save_path,
    )

    if not labels:
        labels = annotation.labels

    annotation._save()

    df = pd.read_csv(save_path, sep=";")

    assert "document" in df.columns
    assert "labels" in df.columns

    assert df.document.to_list() == corpus
    assert df.labels.apply(ast.literal_eval).to_list() == labels


@pytest.mark.parametrize(
    "labels",
    [
        ["O", "O", "O", "O"],
        ["B-2", "I-2", "O", "O"],
        ["B-2", "B-2", "B-2", "B-2"],
    ],
)
def test_clear(labels):
    corpus = ["Test"]
    annotation = Annotation(
        corpus,
        labels=[labels],
    )

    assert annotation.chunks.to_labels() == labels
    assert annotation.labels[0] == labels

    annotation._clear_current(None)

    assert annotation.chunks.to_labels() == ["O", "O", "O", "O"]


def test_additional_infos():
    additional_infos = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    corpus = ["Test 1", "Test 2"]
    annotation = Annotation(
        corpus,
        additional_infos=additional_infos,
    )

    assert annotation.additional_infos.shape == (2, 2)
    assert annotation.additional_infos.col1.to_list() == additional_infos.col1.to_list()
    assert annotation.additional_infos.col2.to_list() == additional_infos.col2.to_list()


@pytest.mark.parametrize(
    "additional_outputs_elements, additional_outputs_values, new_value, expected",
    [
        (
            [
                AdditionalOutputElement(
                    name="element",
                    display_type="text",
                    description="Test element",
                    default_value="testing",
                )
            ],
            None,
            None,
            "testing",
        ),
        (
            [
                AdditionalOutputElement(
                    name="element",
                    display_type="text",
                    description="Test element",
                    default_value="testing",
                )
            ],
            pd.DataFrame(
                {"element": ["input additional value 1", "input additional value 2"]}
            ),
            None,
            "input additional value 1",
        ),
        (
            [
                AdditionalOutputElement(
                    name="element",
                    display_type="text",
                    description="Test element",
                    default_value="testing",
                )
            ],
            None,
            "new_value",
            "new_value",
        ),
        (
            [
                AdditionalOutputElement(
                    name="element",
                    display_type="text",
                    description="Test element",
                    default_value="testing",
                )
            ],
            pd.DataFrame(
                {"element": ["input additional value 1", "input additional value 2"]}
            ),
            "new_value",
            "new_value",
        ),
    ],
)
def test_additional_outputs(
    additional_outputs_elements, additional_outputs_values, new_value, expected
):
    corpus = ["Test 1", "Test 2"]
    save_path = "/tmp/" + str(datetime.now()).replace(" ", "_")
    annotation = Annotation(
        corpus,
        additional_outputs_elements=additional_outputs_elements,
        additional_outputs_values=additional_outputs_values,
        save_path=save_path,
    )

    assert len(annotation.additional_outputs_elements_displays) == 1
    assert annotation.additional_outputs_values.shape == (2, 1)

    if new_value:
        annotation.additional_outputs_elements_displays[0].value = new_value

    # Change document to save it
    annotation._change_document(None, direction=1)

    assert annotation.additional_outputs_values.iloc[0]["element"] == expected

    # Assess that the outputs are correctly added
    annotation._save()

    df = pd.read_csv(save_path, sep=";")

    assert "document" in df.columns
    assert "labels" in df.columns
    assert "element" in df.columns

    assert len(df.element.to_list()) == 2
    assert df.element.to_list()[0] == expected

    if additional_outputs_values is not None:
        assert df.element.to_list()[1] == additional_outputs_values.iloc[1]["element"]
    else:
        assert pd.isna(df.element.to_list()[1])
