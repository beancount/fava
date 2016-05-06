from pathlib import Path

from babel.messages.pofile import read_po


def test_translation_coverage():
    p = Path('./fava/translations/')
    for po_file in list(p.glob('**/*.po')):
        with po_file.open() as file:
            catalog = read_po(file)

        translated = 0
        for message in list(catalog)[1:]:
            if message.string:
                translated += 1

        assert translated / len(catalog) == 1, \
            "Only {}% ({} of {}) messages are translated in {}".format(
                translated * 100 // len(catalog), translated, len(catalog),
                po_file
            )
