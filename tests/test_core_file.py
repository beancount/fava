from __future__ import annotations

import datetime
import os
import re
import shutil
from datetime import date
from hashlib import sha256
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from fava.beans import create
from fava.beans.funcs import get_position
from fava.beans.funcs import hash_entry
from fava.beans.helpers import replace
from fava.core import FavaLedger
from fava.core.fava_options import InsertEntryOption
from fava.core.file import _file_newline_character
from fava.core.file import _incomplete_sortkey
from fava.core.file import ExternallyChangedError
from fava.core.file import find_entry_lines
from fava.core.file import get_entry_slice
from fava.core.file import insert_entry
from fava.core.file import insert_metadata_in_file
from fava.core.file import InvalidUnicodeError
from fava.core.file import NonSourceFileError
from fava.core.file import save_entry_slice

if TYPE_CHECKING:  # pragma: no cover
    from .conftest import SnapshotFunc


@pytest.fixture
def ledger_in_tmp_path(test_data_dir: Path, tmp_path: Path) -> FavaLedger:
    """Create a FavaLedger 'edit-example.beancount' in a tmp_path."""
    ledger_path = tmp_path / "edit-example.beancount"
    shutil.copy(test_data_dir / "edit-example.beancount", ledger_path)
    ledger_path.chmod(tmp_path.stat().st_mode)
    return FavaLedger(str(ledger_path))


def test_sort_incomplete_sortkey() -> None:
    assert sorted([], key=_incomplete_sortkey) == []

    date = datetime.date(2000, 1, 1)

    open_ = create.open(meta={}, date=date, account="Assets", currencies=[])
    balance = create.balance(
        meta={}, date=date, account="Assets", amount=create.amount("10 EUR")
    )
    txn = create.transaction(
        meta={}, date=date, flag="*", payee="payee", narration="narration"
    )
    note = create.note(meta={}, date=date, account="Assets", comment="a note")
    document = create.document(
        meta={}, date=date, account="Assets", filename=""
    )
    close = create.close(meta={}, date=date, account="Assets")

    assert sorted([txn, note], key=_incomplete_sortkey) == [txn, note]
    assert sorted(
        [balance, txn, close, open_, note, document], key=_incomplete_sortkey
    ) == [
        open_,
        balance,
        txn,
        note,
        document,
        close,
    ]


def test_get_and_save_entry_slice(ledger_in_tmp_path: FavaLedger) -> None:
    entry = ledger_in_tmp_path.all_entries[-1]
    entry_hash = hash_entry(entry)
    path = Path(ledger_in_tmp_path.beancount_file_path)

    slice_string, sha256sum = get_entry_slice(entry)
    assert (
        slice_string
        == """2016-05-03 * "Chichipotle" "Eating out with Joe"
  Liabilities:US:Chase:Slate                       -21.70 USD
  Expenses:Food:Restaurant                          21.70 USD"""
    )
    assert (
        sha256sum
        == "d60da810c0c7b8a57ae16be409c5e17a640a837c1ac29719ebe9f43930463477"
    )

    new_slice = """2016-05-03 * "Chichipotle" "Eating out with Joe"
  document: "doc"
  Liabilities:US:Chase:Slate                       -21.70 USD
  Expenses:Food:Restaurant                          21.70 USD
"""
    ledger_in_tmp_path.file.save_entry_slice(entry_hash, new_slice, sha256sum)
    assert new_slice in path.read_text("utf-8")


def test_windows_newlines(ledger_in_tmp_path: FavaLedger) -> None:
    path = Path(ledger_in_tmp_path.beancount_file_path)
    contents = path.read_text("utf-8")
    assert "\r\n" not in contents
    source, sha256sum = ledger_in_tmp_path.file.get_source(path)

    # unix newlines are used if already present
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(contents)
    ledger_in_tmp_path.file.set_source(path, source, sha256sum)
    assert _file_newline_character(path) == "\n"
    assert "\r\n" not in path.read_text("utf-8")

    # write empty file
    path.write_bytes(b"")
    assert _file_newline_character(path) == os.linesep

    # write to file with windows newlines
    with path.open("w", encoding="utf-8", newline="\r\n") as file:
        file.write(contents)
    assert _file_newline_character(path) == "\r\n"
    assert b"\r\n" in path.read_bytes()
    source, _sha256sum = ledger_in_tmp_path.file.get_source(path)
    assert "\r\n" not in source
    assert source == contents


def test_get_and_set_source(ledger_in_tmp_path: FavaLedger) -> None:
    with pytest.raises(NonSourceFileError):
        ledger_in_tmp_path.file.get_source(Path("asdf"))

    path = Path(ledger_in_tmp_path.beancount_file_path)
    source, sha256sum = ledger_in_tmp_path.file.get_source(path)
    assert source == path.read_text("utf-8")

    with pytest.raises(ExternallyChangedError):
        ledger_in_tmp_path.file.set_source(path, "test", "notasha256sum")

    new_sha256sum = ledger_in_tmp_path.file.set_source(path, "test", sha256sum)
    assert path.read_text("utf-8") == "test"
    assert new_sha256sum == sha256(b"test").hexdigest()

    path.write_bytes(b"\xc3\x28")
    with pytest.raises(InvalidUnicodeError):
        ledger_in_tmp_path.file.get_source(path)


def test_insert_metadata(ledger_in_tmp_path: FavaLedger) -> None:
    entry = ledger_in_tmp_path.all_entries[-1]
    entry_hash = hash_entry(entry)
    path = Path(ledger_in_tmp_path.beancount_file_path)

    ledger_in_tmp_path.file.insert_metadata(entry_hash, "document", "doc")
    assert ledger_in_tmp_path.watcher.check()
    assert path.read_text("utf-8").endswith(
        """2016-05-03 * "Chichipotle" "Eating out with Joe"
  document: "doc"
  Liabilities:US:Chase:Slate                       -21.70 USD
  Expenses:Food:Restaurant                          21.70 USD
"""
    )


def test_save_entry_slice(ledger_in_tmp_path: FavaLedger) -> None:
    entry = ledger_in_tmp_path.all_entries[-1]

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


def test_delete_entry_slice(ledger_in_tmp_path: FavaLedger) -> None:
    entry = ledger_in_tmp_path.all_entries[-1]
    entry_hash = hash_entry(entry)

    _entry_source, sha256sum = get_entry_slice(entry)
    path = Path(get_position(entry)[0])
    contents = path.read_text("utf-8")

    with pytest.raises(ExternallyChangedError):
        ledger_in_tmp_path.file.delete_entry_slice(entry_hash, "wrong hash")
    assert not ledger_in_tmp_path.watcher.check()
    assert path.read_text("utf-8") == contents
    assert '2016-05-03 * "Chichipotle" "Eating out with Joe"' in contents

    ledger_in_tmp_path.file.delete_entry_slice(entry_hash, sha256sum)
    assert ledger_in_tmp_path.watcher.check()
    assert (
        '2016-05-03 * "Chichipotle" "Eating out with Joe"'
        not in path.read_text("utf-8")
    )


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
        create.posting("Liabilities:US:Chase:Slate", "-10.00 USD"),
        create.posting("Expenses:Food", "10.00 USD"),
    ]

    transaction = create.transaction(
        {},
        date(2016, 1, 1),
        "*",
        "new payee",
        "narr",
        postings=postings,
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
            date(2015, 1, 1), re.compile(r".*:Food"), str(samplefile), 1
        ),
        InsertEntryOption(
            date(2015, 1, 2), re.compile(r".*:FOOO"), str(samplefile), 1
        ),
        InsertEntryOption(
            date(2017, 1, 1), re.compile(r".*:Food"), str(samplefile), 6
        ),
    ]
    path, new_options = insert_entry(
        replace(transaction, narration="narr1"),
        str(samplefile),
        options,
        61,
        4,
    )
    assert path == samplefile
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
            date(2015, 1, 1), re.compile(r".*:Slate"), str(samplefile), 5
        ),
        InsertEntryOption(
            date(2015, 1, 2), re.compile(r".*:FOOO"), str(samplefile), 1
        ),
    ]
    new_transaction = replace(transaction, narration="narr2")
    path, new_options = insert_entry(
        new_transaction,
        str(samplefile),
        options,
        61,
        4,
    )
    assert path == samplefile
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
            date(2015, 1, 1), re.compile(r".*:Food"), str(samplefile), 5
        ),
        InsertEntryOption(
            date(2015, 1, 2), re.compile(r".*:Food"), str(samplefile), 1
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
        create.posting("Liabilities:US:Chase:Slate", "-10.00 USD"),
        create.posting("Expenses:Food", "10.00 USD"),
    ]

    transaction = create.transaction(
        {},
        date(2016, 1, 1),
        "*",
        "new payee",
        "narr",
        postings=postings,
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
        create.posting("Liabilities:US:Chase:Slate", "-10.00 USD"),
        create.posting("Expenses:Food", "10.00 USD"),
    ]

    transaction = create.transaction(
        {},
        date(2016, 1, 1),
        "*",
        "new payee",
        "narr",
        postings=postings,
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
    small_example_ledger: FavaLedger,
    snapshot: SnapshotFunc,
) -> None:
    all_transactions = small_example_ledger.all_entries_by_type.Transaction
    entry1 = all_transactions[2]
    entry2 = all_transactions[3]
    transaction = create.transaction(
        {},
        date(2016, 1, 1),
        "*",
        "new payee",
        "narr",
        postings=[
            create.posting("Expenses:Food", "10.00 USD"),
        ],
    )
    entries = list(
        small_example_ledger.file.render_entries([entry1, entry2, transaction])
    )
    assert len(entries) == 3
    snapshot("\n".join(entries))
