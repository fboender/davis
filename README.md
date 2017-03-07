(Py)Davis: Python Data Visualizer
=================================

Davis is a data visualizer for Python. The goal is to make something better
and easier to use than `print()` and `pprint()` for inspecting data structures
in Python.

Davis can currently visualize Python data structures and JSON from running
Python programs or from files.

Here's what it looks like:

![](https://raw.githubusercontent.com/fboender/davis/master/contrib/scrsht_main.png)

## Installation

FIXME

## Usage

As a library for inspecting data in running Python programs:

    my_data = {'alist': [{'pos': 0}, {'pos': 1}], 'adict': {'a': 'a string'}}

    import davis
    davis.vis(my_data)

This will pause the execution of your program at the call to `davis.vis()` and
pop-up a window that lets you inspect `my_data`:

![](https://raw.githubusercontent.com/fboender/davis/master/contrib/scrsht_inline.png)

You can also invoke Davis from the command-line to load data from STDIN or a
file:

    $ wget -O r_programming.json https://www.reddit.com/r/programming/.json
    $ davis.py r_programming.json

Or from STDIN:

    $ wget -O - https://www.reddit.com/r/programming/.json | davis.py

