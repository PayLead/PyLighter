import pytest

from pylighter import utils


def test_text_parser():
    args = {
        "shift_key": "false",
        "alt_key": "true",
        "ctrl_key": "false",
        "key": "œ",
        "class_name": "test_class_name",
    }

    text_parsed = utils.text_parser("js/key_shortcut.js", **args)
    expected_text_parsed = """
if (
    e.shiftKey == false
    && e.altKey == true
    && e.ctrlKey == false
    && e.key == "œ"
) {
    let button = document.getElementsByClassName("test_class_name")[0];
    button.click();
}""".replace(
        "\n", ""
    )

    assert text_parsed == expected_text_parsed


@pytest.mark.parametrize(
    "text, expected",
    [("A chunk", "A chunk"), ("A chunk ", "A chunk␣"), (" ", "␣"), ("", "")],
)
def test_chunk_html_display(text, expected):
    assert utils.chunk_html_display(text) == expected


@pytest.mark.parametrize(
    "color, expected",
    [
        ("#2DA9D5", "hsl(195, 66%, 40%)"),  # hsl(195, 66%, 51%)
        ("#FFC366", "hsl(36, 100%, 55%)"),  # hsl(36, 100%, 69%)
        ("#50C78E", "hsl(151, 51%, 43%)"),  # hsl(151, 51%, 54%)
    ],
)
def test_compute_selected_label_color(color, expected):
    assert utils.compute_selected_label_color(color) == expected


@pytest.mark.parametrize(
    "display_type, expected_error",
    [
        ("checkbox", False),
        ("checkboxe", True),
        ("int_area", True),
        ("int_text", False),
        ("float_text", False),
        ("text", False),
        ("text_area", False),
    ],
)
def test_AdditionalOutputElement(display_type, expected_error):
    args = {
        "name": "element",
        "display_type": display_type,
        "description": "testing element",
        "default_value": 42,
    }
    if expected_error:
        with pytest.raises(ValueError):
            utils.AdditionalOutputElement(**args)
    else:
        assert utils.AdditionalOutputElement(**args)


@pytest.mark.parametrize(
    "labels, expects_assert_error",
    [
        ([], False),
        (["O"], False),
        (["O", "O", "O", "O"], False),
        (["B-1", "O", "O", "O"], False),
        (["O", "B-1", "O", "O"], False),
        (["O", "B-1", "B-2", "O"], False),
        (["B-1", "I-1", "B-2", "O"], False),
        (["B-1", "B-1", "B-1", "B-1"], False),
        (["B-1", "I-1", "I-1", "I-1"], False),
        (["B-1", "I-2", "I-1", "I-1"], True),
        (["O", "I-1", "O", "O"], True),
        (["O", "I-1", "I-1", "I-1"], True),
        (["O", "A-1", "O", "O"], True),
    ],
)
def test_assert_IOB2_format(labels, expects_assert_error):
    if expects_assert_error:
        with pytest.raises(AssertionError):
            utils.assert_IOB2_format([labels])
    else:
        utils.assert_IOB2_format([labels])
