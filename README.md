# fava

Web interface for the double-entry bookkeeping software
[beancount](http://furius.ca/beancount/) with a focus on features and usability.

You can try out a demo here: [fava.pythonanywhere.com](http://fava.pythonanywhere.com)

[![fava](https://raw.githubusercontent.com/aumayr/fava/master/util/screenshots/screenshot-01.png)](#screenshot)
(More Screenshots here: [github.com/aumayr/fava/tree/master/util/screenshots](https://github.com/aumayr/fava/tree/master/util/screenshots))

## Installation

1. Prerequisites: An installed version of
   [beancount](http://furius.ca/beancount/) and Python >= 3.5
3. Install it from PyPI by running `pip3 install beancount-fava`

## Usage

1. Start `fava` by running `fava
   /Volumes/Ledger/example.ledger` (substitute with the path to your own
   beancount-file) to run the included web server.
2. Point your browser at `http://localhost:5000` to view the web interface.

`fava` comes with Gmail-style keyboard shortcuts: Press <kbd>?</kbd> to show an overview of the keyboard shortcuts.

## Development

If you want to hack on `fava`, this will get you up and running:

    git clone https://github.com/aumayr/fava.git
    cd fava
    # using a virtual environment is optional, but recommended
    virtualenv -p python3 venv
    . venv/bin/activate
    make build-js
    pip install --editable .

Note that you'll need to have `npm` installed to build the Javascript UI.

---
**Caution**: Consider this *beta*-software. Contributions are very welcome :-)
