# PyLighter: Annotation tool for NER tasks

PyLighter is a tool that allows data scientists to annotate a corpus of documents directly on Jupyter for NER (Named Entity Recognition) tasks.

<span style="display:block;text-align:center">
<img src="https://github.com/PayLead/PyLighter/blob/master/media/pylighter.gif" alt="pylighter_gif"/>
</span>

## Contents

- [Installation](#installation)
- [Basic usage](#basic-usage)
- [Advanced usage](#advanced-usage)
    - [Using an already annotated corpus](#using-an-already-annotated-corpus)
    - [Changing labels names](#changing-labels-names)
    - [Document styling](#document-styling)
    - [Adding additional information](#adding-additional-information)
    - [Adding additional outputs](#adding-additional-outputs)
    - [Using keyboard shortcuts](#using-keyboard-shortcuts)
- [Testing](#testing)
<!-- - [Contributing](#contributing) -->
- [License](#license)
<!-- - [Credits](#credits) -->

## Installation

Pypi: [url](url)

```
pip install pylighter
```

Source: [https://github.com/PayLead/PyLighter](https://github.com/PayLead/PyLighter)
```
git clone git@github.com:PayLead/PyLighter.git
cd PyLighter
python setup.py install
```

## Demos

The [demo](https://github.com/PayLead/PyLighter/tree/master/demo) folder contains working examples of PyLighter in use. To view them, open any of the ipynb files in Jupyter.

## Basic usage

The use case of PyLighter is to easily annotate a corpus in Jupyter. So let's first define a corpus for this example:

```python
corpus = [
    "PyLighter is an annotation tool for NER tasks directly on Jupyter. " 
    + "It aims on helping data scientists easily and quickly annotate datasets. "
    + "This tool was developed by Paylead.",
    "PayLead is a fintech company specializing in transaction data analysis. "
    + "Paylead brings retail and banking together, so customers get rewarded when they buy. " 
    + "Welcome to the data-for-value economy."
]
```

Now let's start annotating !

```python
from pylighter import Annotation

annotation = Annotation(corpus)
```

Running that cell gives you the following output:

![screenshot_basic_usage.png](https://github.com/PayLead/PyLighter/blob/master/media/screenshot_basic_usage.png)

You can know start annotating entities using the predefined labels _l1_, _l2_, etc. 

When your annotation is finished, you can either click on the save button or retrieve the results in the current Notebook. 
- The save button will save the results in a csv file named _annotation.csv_ with two columns: the documents and the labels.
- You can access the labels of your annotations in `annotation.labels`

Note: The given labels are in IOB2 format. 

## Advanced usage

The above example works just fine but PyLighter can be customized to best fit your specific use case.

### Using an already annotated corpus

In most cases, you want to use an already annotated corpus or simply continue your annotation.

To this, you can use the argument named `labels` with the labels of the corpus. Moreover, if you stopped at the i<sup>th</sup> document, you can directly get back to where you stopped with `start_index=i`.

![screenshot_pre_annotated](https://github.com/PayLead/PyLighter/blob/master/media/screenshot_pre_annotated.png)

You can see more on that with [this](https://github.com/PayLead/PyLighter/blob/master/demo/Annotated_corpus.ipynb) demo.

### Changing labels names

PyLighter uses _l1_, _l2_, ...., _l7_ as default labels names, but in most cases, you want to have explicit labels such as _Noun_, _Verb_, etc. 

You can define your own labels names with the argument `labels_names`. You can also define your own colors for your labels with the argument `labels_colors` in HEX format.

![screenshot_labels_changed](https://github.com/PayLead/PyLighter/blob/master/media/screenshot_labels_changed.png)

You can see more on that with [this](https://github.com/PayLead/PyLighter/blob/master/demo/Simple_usage.ipynb) demo.

### Document styling

You can adjust the font size, the minimal distance between two characters and the size of spaces with the argument `char_params`.

Default value for char_params is:
```python
# Each field expects css value as a string (ex:"10px", "1em", "large", etc.)
char_params = {
    "font_size": "medium", 
    "width_white_space": "1Opx",
    "min_width_between_chars": "4px",
}
```

### Adding additional information

In some cases, you may want to know additional information about the current document, such as the source of it.

To do this, you can use the argument `additional_infos`. This argument must be a pandas DataFrame of shape (_size of the corpus_, _number of additional information_). The i<sup>th</sup> row of the DataFrame will be associated with the i<sup>th</sup> element of the corpus.

The elements of the given DataFrame need to have a proper string representation to be correctly displayed.

For instance, to add the source to each element of the corpus:
```python
import pandas as pd

# define corpus of size 2
additional_infos = pd.DataFrame({"source":["Github", "Paylead.fr"]})
annotation = Annotation(corpus, additional_infos=additional_infos)
```

The result will be:

![screenshot_additional_information](https://github.com/PayLead/PyLighter/blob/master/media/screenshot_additional_information.png)

You can see more on that with [this](https://github.com/PayLead/PyLighter/blob/master/demo/Adding_additional_elements.ipynb) demo.

### Adding additional outputs

In some cases, you want to flag a document as difficult to annotate, or spot as wrong, or give a value that estimates your confidence in your annotation, etc. In short, you need to return additional information.

To do this, you can use the argument: `additional_outputs_elements`. This argument expects a list of `pylighter.AdditionalOutputElement`.

A `pylighter.AdditionalOutputElement` is defined like this:
```python
from pyligher import AdditionalOutputElement

AdditionalOutputElement(
    name="name_of_my_element",
    display_type="type_of_display" # checkbox, int_text, float_text, text, text_area
    description="Description of the element to display",
    default_value="Default value for the element"
)
```

Here is an example:

![screenshot_additional_outputs](https://github.com/PayLead/PyLighter/blob/master/media/screenshot_additional_outputs.png)

Note: Additional outputs will be added to the save file. But you can also retrieve them with `annotation.additional_outputs_values`. You can also use previously returned additional outputs values with the argument: `additional_outputs_values` (same as the label).

You can see more on that with [this](https://github.com/PayLead/PyLighter/blob/master/demo/Adding_additional_elements.ipynb) demo.

### Using keyboard shortcuts

Annotation tasks are pretty boring. Thus you may want to use keyboard shortcuts to easily change documents or to select an other label.

By default, there are only a few shortcuts defined:
- next: **Alt + n**
- previous: **Alt + p**
- skip: **Alt + s**
- save: **Shift + Alt + s**

However, you can fully customize them with the arguments: `standard_shortcuts` and `labels_shorcuts`. The `standard_shortcuts` argument is used to redefined shortcuts for the standard buttons such as the next button whereas the 

A shortcut is defined like this:
```python
from pylighter import Shortcut

Shortcut(
    name="skip",  # Name of the button to bind on (ex: "next", "skip") or name of the label (ex: "l1", "l2", or one you defined)
    key="Ò",  # Usually represents the character that is displayed.
    code="KeyS",  # Usually represents the key that is pressed.
    shift_key=False,  # Wether the shift key is pressed
    alt_key=True,
    ctrl_key=False
)
```

It is pretty hard to know what is the value for the `key` and the value for the `code`. It depends on a lot of different factors such as your keyboard, your browser, etc.

Thus, you can use the `ShortcutHelper` to pick the right shortcut. Here is an example of it.

```python
from pylighter import ShortcutHelper

ShortcutHelper()
```

![screenshot_shortcut_helper](https://github.com/PayLead/PyLighter/blob/master/media/screenshot_shortcut_helper.ipynb)

You can see more on that with [this](https://github.com/PayLead/PyLighter/blob/master/demo/Shortcut_helper.ipynb) demo.

<!-- ### Full Api

Parse annotation docstring and put it here ? -->

## Testing

PyLighter uses _pytest_. Thus, tests can be run with:
```
pytest tests/*
```

<!-- ## Contributing

Currently nothing has be done there -->

## License

MIT License

<!-- ## Credits -->

