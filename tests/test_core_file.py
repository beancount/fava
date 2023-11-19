from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from fava.beans import create
from fava.beans.funcs import get_position
from fava.beans.helpers import replace
from fava.core.fava_options import InsertEntryOption
from fava.core.file import delete_entry_slice
from fava.core.file import ExternallyChangedError
from fava.core.file import find_entry_lines
from fava.core.file import get_entry_slice
from fava.core.file import insert_entry
from fava.core.file import insert_metadata_in_file
from fava.core.file import save_entry_slice

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Transaction
    from fava.core import FavaLedger

    from .conftest import SnapshotFunc


def _get_entry(ledger: FavaLedger, payee: str, date_: str) -> Transaction:
    """Fetch a transaction with the given payee and date."""
    return next(
        e
        for e in ledger.all_entries_by_type.Transaction
        if e.payee == payee and str(e.date) == date_
    )


def test_get_entry_slice(example_ledger: FavaLedger) -> None:
    entry = _get_entry(example_ledger, "Chichipotle", "2016-05-03")

    assert get_entry_slice(entry) == (
        """2016-05-03 * "Chichipotle" "Eating out with Joe"
  Liabilities:US:Chase:Slate                       -21.70 USD
  Expenses:Food:Restaurant                          21.70 USD""",
        "d60da810c0c7b8a57ae16be409c5e17a640a837c1ac29719ebe9f43930463477",
    )


def test_save_entry_slice(example_ledger: FavaLedger) -> None:
    entry = _get_entry(example_ledger, "Chichipotle", "2016-05-03")

    entry_source, sha256sum = get_entry_slice(entry)
    new_source = """2016-05-03 * "Chichipotle" "Eating out with Joe"
  Expenses:Food:Restaurant                          21.70 USD"""
    filename = Path(get_position(entry)[0])
    contents = filename.read_text("utf-8")

    with pytest.raises(ExternallyChangedError):
        save_entry_slice(entry, new_source, "wrong hash")
    assert filename.read_text("utf-8") == contents

    new_sha256sum = save_entry_slice(entry, new_source, sha256sum)
    assert filename.read_text("utf-8") != contents
    sha256sum = save_entry_slice(entry, entry_source, new_sha256sum)
    assert filename.read_text("utf-8") == contents


def test_delete_entry_slice(example_ledger: FavaLedger) -> None:
    entry = _get_entry(example_ledger, "Chichipotle", "2016-05-03")

    _entry_source, sha256sum = get_entry_slice(entry)
    filename, lineno = get_position(entry)
    path = Path(filename)
    contents = path.read_text("utf-8")

    with pytest.raises(ExternallyChangedError):
        delete_entry_slice(entry, "wrong hash")
    assert path.read_text("utf-8") == contents

    delete_entry_slice(entry, sha256sum)
    assert path.read_text("utf-8") != contents

    insert_option = InsertEntryOption(
        date(1, 1, 1),
        re.compile(".*"),
        filename,
        lineno,
    )
    insert_entry(entry, filename, [insert_option], 59, 2)
    assert path.read_text("utf-8") == contents


def test_insert_metadata_in_file(tmp_path: Path) -> None:
    file_content = dedent("""\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
        """)
    samplefile = tmp_path / "example.beancount"
    samplefile.write_text(file_content)

    # Insert some metadata lines.
    insert_metadata_in_file(samplefile, 1, 4, "metadata", "test1")
    insert_metadata_in_file(samplefile, 1, 4, "metadata", "test2")
    assert samplefile.read_text("utf-8") == dedent("""\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            metadata: "test2"
            metadata: "test1"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
        """)

    # Check that inserting also works if the next line is empty.
    insert_metadata_in_file(samplefile, 5, 4, "metadata", "test1")
    assert samplefile.read_text("utf-8") == dedent("""\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            metadata: "test2"
            metadata: "test1"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
            metadata: "test1"
        """)


def test_find_entry_lines() -> None:
    file_content = dedent("""\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD

        2016-02-26 note Accounts:Text "Uncle Boons"
        2016-02-26 note Accounts:Text "Uncle Boons"
        ; test
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
        """)
    lines = file_content.split("\n")
    entry_lines = [
        '2016-02-26 * "Uncle Boons" "Eating out alone"',
        "    Liabilities:US:Chase:Slate                       -24.84 USD",
        "    Expenses:Food:Restaurant                          24.84 USD",
    ]
    note_line = ['2016-02-26 note Accounts:Text "Uncle Boons"']
    assert find_entry_lines(lines, 0) == entry_lines
    assert find_entry_lines(lines, 7) == entry_lines
    assert find_entry_lines(lines, 4) == note_line
    assert find_entry_lines(lines, 5) == note_line


def test_insert_entry_transaction(tmp_path: Path) -> None:
    file_content = dedent("""\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
        """)
    samplefile = tmp_path / "example.beancount"
    samplefile.write_text(file_content)

    postings = [
        create.posting(
            "Liabilities:US:Chase:Slate",
            "-10.00 USD",
        ),
        create.posting("Expenses:Food", "10.00 USD"),
    ]

    transaction = create.transaction(
        {},
        date(2016, 1, 1),
        "*",
        "new payee",
        "narr",
        frozenset(),
        frozenset(),
        postings,
    )

    # Test insertion without "insert-entry" options.
    insert_entry(transaction, str(samplefile), [], 61, 4)
    assert samplefile.read_text("utf-8") == dedent("""\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD

        2016-01-01 * "new payee" "narr"
            Liabilities:US:Chase:Slate                       -10.00 USD
            Expenses:Food                                     10.00 USD
        """)

    # Verify that InsertEntryOptions with dates greater or equal than the
    # transaction dates are ignored.
    options = [
        InsertEntryOption(
            date(2015, 1, 1),
            re.compile(".*:Food"),
            str(samplefile),
            1,
        ),
        InsertEntryOption(
            date(2015, 1, 2),
            re.compile(".*:FOOO"),
            str(samplefile),
            1,
        ),
        InsertEntryOption(
            date(2017, 1, 1),
            re.compile(".*:Food"),
            str(samplefile),
            6,
        ),
    ]
    new_options = insert_entry(
        replace(transaction, narration="narr1"),
        str(samplefile),
        options,
        61,
        4,
    )
    assert new_options[0].lineno == 5
    assert new_options[1].lineno == 5
    assert new_options[2].lineno == 10
    assert samplefile.read_text("utf-8") == dedent("""\
        2016-01-01 * "new payee" "narr1"
            Liabilities:US:Chase:Slate                       -10.00 USD
            Expenses:Food                                     10.00 USD

        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD

        2016-01-01 * "new payee" "narr"
            Liabilities:US:Chase:Slate                       -10.00 USD
            Expenses:Food                                     10.00 USD
        """)

    # Verify that previous postings are matched against InsertEntryOptions when
    # the last posting doesn't match.
    options = [
        InsertEntryOption(
            date(2015, 1, 1),
            re.compile(".*:Slate"),
            str(samplefile),
            5,
        ),
        InsertEntryOption(
            date(2015, 1, 2),
            re.compile(".*:FOOO"),
            str(samplefile),
            1,
        ),
    ]
    new_transaction = replace(transaction, narration="narr2")
    new_options = insert_entry(
        new_transaction,
        str(samplefile),
        options,
        61,
        4,
    )
    assert new_options[0].lineno == 9
    assert new_options[1].lineno == 1
    assert samplefile.read_text("utf-8") == dedent("""\
        2016-01-01 * "new payee" "narr1"
            Liabilities:US:Chase:Slate                       -10.00 USD
            Expenses:Food                                     10.00 USD

        2016-01-01 * "new payee" "narr2"
            Liabilities:US:Chase:Slate                       -10.00 USD
            Expenses:Food                                     10.00 USD

        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD

        2016-01-01 * "new payee" "narr"
            Liabilities:US:Chase:Slate                       -10.00 USD
            Expenses:Food                                     10.00 USD
        """)

    # Verify that preference is given to InsertEntryOptions with later dates in
    # case several of them match a posting.
    options = [
        InsertEntryOption(
            date(2015, 1, 1),
            re.compile(".*:Food"),
            str(samplefile),
            5,
        ),
        InsertEntryOption(
            date(2015, 1, 2),
            re.compile(".*:Food"),
            str(samplefile),
            1,
        ),
    ]
    new_transaction = replace(transaction, narration="narr3")
    insert_entry(new_transaction, str(samplefile), options, 61, 4)
    assert samplefile.read_text("utf-8") == dedent("""\
        2016-01-01 * "new payee" "narr3"
            Liabilities:US:Chase:Slate                       -10.00 USD
            Expenses:Food                                     10.00 USD

        2016-01-01 * "new payee" "narr1"
            Liabilities:US:Chase:Slate                       -10.00 USD
            Expenses:Food                                     10.00 USD

        2016-01-01 * "new payee" "narr2"
            Liabilities:US:Chase:Slate                       -10.00 USD
            Expenses:Food                                     10.00 USD

        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD

        2016-01-01 * "new payee" "narr"
            Liabilities:US:Chase:Slate                       -10.00 USD
            Expenses:Food                                     10.00 USD
        """)


def test_insert_entry_align(tmp_path: Path) -> None:
    file_content = dedent("""\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
        """)
    samplefile = tmp_path / "example.beancount"
    samplefile.write_text(file_content)

    postings = [
        create.posting(
            "Liabilities:US:Chase:Slate",
            "-10.00 USD",
        ),
        create.posting("Expenses:Food", "10.00 USD"),
    ]

    transaction = create.transaction(
        {},
        date(2016, 1, 1),
        "*",
        "new payee",
        "narr",
        frozenset(),
        frozenset(),
        postings,
    )

    insert_entry(transaction, str(samplefile), [], 50, 4)
    assert samplefile.read_text("utf-8") == dedent("""\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD

        2016-01-01 * "new payee" "narr"
            Liabilities:US:Chase:Slate            -10.00 USD
            Expenses:Food                          10.00 USD
        """)


def test_insert_entry_indent(tmp_path: Path) -> None:
    file_content = dedent("""\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD
        """)
    samplefile = tmp_path / "example.beancount"
    samplefile.write_text(file_content)

    postings = [
        create.posting(
            "Liabilities:US:Chase:Slate",
            "-10.00 USD",
        ),
        create.posting("Expenses:Food", "10.00 USD"),
    ]

    transaction = create.transaction(
        {},
        date(2016, 1, 1),
        "*",
        "new payee",
        "narr",
        frozenset(),
        frozenset(),
        postings,
    )

    # Test insertion with 2-space indent.
    insert_entry(transaction, str(samplefile), [], 61, 2)
    assert samplefile.read_text("utf-8") == dedent("""\
        2016-02-26 * "Uncle Boons" "Eating out alone"
            Liabilities:US:Chase:Slate                       -24.84 USD
            Expenses:Food:Restaurant                          24.84 USD

        2016-01-01 * "new payee" "narr"
          Liabilities:US:Chase:Slate                         -10.00 USD
          Expenses:Food                                       10.00 USD
        """)


def test_render_entries(
    example_ledger: FavaLedger,
    snapshot: SnapshotFunc,
) -> None:
    entry1 = _get_entry(example_ledger, "Uncle Boons", "2016-04-09")
    entry2 = _get_entry(example_ledger, "BANK FEES", "2016-05-04")
    postings = [
        create.posting("Expenses:Food", "10.00 USD"),
    ]
    transaction = create.transaction(
        {},
        date(2016, 1, 1),
        "*",
        "new payee",
        "narr",
        frozenset(),
        frozenset(),
        postings,
    )
    entries = example_ledger.file.render_entries([entry1, entry2, transaction])
    snapshot("\n".join(entries))

    file_content = dedent("""\
        2016-04-09 * "Uncle Boons" "" #trip-new-york-2016
          Liabilities:US:Chase:Slate                       -52.22 USD
          Expenses:Food:Restaurant                          52.22 USD

        2016-05-04 * "BANK FEES" "Monthly bank fee"
          Assets:US:BofA:Checking                           -4.00 USD
          Expenses:Financial:Fees                            4.00 USD
        """)

    assert file_content == "\n".join(
        example_ledger.file.render_entries([entry1, entry2]),
    )
