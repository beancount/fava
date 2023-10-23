"""Reading/writing Beancount files."""

from __future__ import annotations

import re
import threading
from codecs import decode
from codecs import encode
from dataclasses import replace
from hashlib import sha256
from operator import attrgetter
from pathlib import Path
from typing import Iterable
from typing import TYPE_CHECKING

from markupsafe import Markup

from fava.beans.abc import Balance
from fava.beans.abc import Close
from fava.beans.abc import Document
from fava.beans.abc import Open
from fava.beans.abc import Transaction
from fava.beans.account import get_entry_accounts
from fava.beans.flags import FLAG_CONVERSIONS
from fava.beans.flags import FLAG_MERGING
from fava.beans.flags import FLAG_PADDING
from fava.beans.flags import FLAG_RETURNS
from fava.beans.flags import FLAG_SUMMARIZE
from fava.beans.flags import FLAG_TRANSFER
from fava.beans.flags import FLAG_UNREALIZED
from fava.beans.str import to_string
from fava.core.module_base import FavaModule
from fava.helpers import FavaAPIError
from fava.util import next_key

if TYPE_CHECKING:  # pragma: no cover
    import datetime

    from fava.beans.abc import Directive
    from fava.core import FavaLedger
    from fava.core.fava_options import InsertEntryOption

#: The flags to exclude when rendering entries.
EXCL_FLAGS = {
    FLAG_PADDING,  # P
    FLAG_SUMMARIZE,  # S
    FLAG_TRANSFER,  # T
    FLAG_CONVERSIONS,  # C
    FLAG_UNREALIZED,  # U
    FLAG_RETURNS,  # R
    FLAG_MERGING,  # M
}


def sha256_str(val: str) -> str:
    """Hash a string."""
    return sha256(encode(val, encoding="utf-8")).hexdigest()


class NonSourceFileError(FavaAPIError):
    """Trying to read a non-source file."""

    def __init__(self, path: Path) -> None:
        super().__init__(f"Trying to read a non-source file at '{path}'")


class ExternallyChangedError(FavaAPIError):
    """The file changed externally."""

    def __init__(self, path: Path) -> None:
        super().__init__(f"The file at '{path}' changed externally.")


class InvalidUnicodeError(FavaAPIError):
    """The source file contains invalid unicode."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            f"The source file contains invalid unicode: {reason}.",
        )


class FileModule(FavaModule):
    """Functions related to reading/writing to Beancount files."""

    def __init__(self, ledger: FavaLedger) -> None:
        super().__init__(ledger)
        self.lock = threading.Lock()

    def get_source(self, path: Path) -> tuple[str, str]:
        """Get source files.

        Args:
            path: The path of the file.

        Returns:
            A string with the file contents and the `sha256sum` of the file.

        Raises:
            FavaAPIError: If the file at `path` is not one of the
                source files or it contains invalid unicode.
        """
        if str(path) not in self.ledger.options["include"]:
            raise NonSourceFileError(path)

        with path.open(mode="rb") as file:
            contents = file.read()

        sha256sum = sha256(contents).hexdigest()
        try:
            source = decode(contents)
        except UnicodeDecodeError as exc:
            raise InvalidUnicodeError(str(exc)) from exc

        return source, sha256sum

    def set_source(self, path: Path, source: str, sha256sum: str) -> str:
        """Write to source file.

        Args:
            path: The path of the file.
            source: A string with the file contents.
            sha256sum: Hash of the file.

        Returns:
            The `sha256sum` of the updated file.

        Raises:
            FavaAPIError: If the file at `path` is not one of the
                source files or if the file was changed externally.
        """
        with self.lock:
            _, original_sha256sum = self.get_source(path)
            if original_sha256sum != sha256sum:
                raise ExternallyChangedError(path)

            contents = encode(source, encoding="utf-8")
            with path.open("w+b") as file:
                file.write(contents)

            self.ledger.extensions.after_write_source(str(path), source)
            self.ledger.load_file()

            return sha256(contents).hexdigest()

    def insert_metadata(
        self,
        entry_hash: str,
        basekey: str,
        value: str,
    ) -> None:
        """Insert metadata into a file at lineno.

        Also, prevent duplicate keys.
        """
        with self.lock:
            self.ledger.changed()
            entry: Directive = self.ledger.get_entry(entry_hash)
            key = next_key(basekey, entry.meta)
            indent = self.ledger.fava_options.indent
            insert_metadata_in_file(
                Path(entry.meta["filename"]),
                entry.meta["lineno"],
                indent,
                key,
                value,
            )
            self.ledger.extensions.after_insert_metadata(entry, key, value)

    def save_entry_slice(
        self,
        entry_hash: str,
        source_slice: str,
        sha256sum: str,
    ) -> str:
        """Save slice of the source file for an entry.

        Args:
            entry_hash: An entry.
            source_slice: The lines that the entry should be replaced with.
            sha256sum: The sha256sum of the current lines of the entry.

        Returns:
            The `sha256sum` of the new lines of the entry.

        Raises:
            FavaAPIError: If the entry is not found or the file changed.
        """
        with self.lock:
            entry = self.ledger.get_entry(entry_hash)
            ret = save_entry_slice(entry, source_slice, sha256sum)
            self.ledger.extensions.after_entry_modified(entry, source_slice)
            return ret

    def delete_entry_slice(self, entry_hash: str, sha256sum: str) -> None:
        """Delete slice of the source file for an entry.

        Args:
            entry_hash: An entry.
            sha256sum: The sha256sum of the current lines of the entry.

        Raises:
            FavaAPIError: If the entry is not found or the file changed.
        """
        with self.lock:
            entry = self.ledger.get_entry(entry_hash)
            delete_entry_slice(entry, sha256sum)
            self.ledger.extensions.after_delete_entry(entry)

    def insert_entries(self, entries: list[Directive]) -> None:
        """Insert entries.

        Args:
            entries: A list of entries.
        """
        with self.lock:
            self.ledger.changed()
            fava_options = self.ledger.fava_options
            for entry in sorted(entries, key=incomplete_sortkey):
                insert_options = fava_options.insert_entry
                currency_column = fava_options.currency_column
                indent = fava_options.indent
                fava_options.insert_entry = insert_entry(
                    entry,
                    self.ledger.beancount_file_path,
                    insert_options,
                    currency_column,
                    indent,
                )
                self.ledger.extensions.after_insert_entry(entry)

    def render_entries(self, entries: list[Directive]) -> Iterable[Markup]:
        """Return entries in Beancount format.

        Only renders :class:`.Balance` and :class:`.Transaction`.

        Args:
            entries: A list of entries.

        Yields:
            The entries rendered in Beancount format.
        """
        indent = self.ledger.fava_options.indent
        for entry in entries:
            if isinstance(entry, (Balance, Transaction)):
                if isinstance(entry, Transaction) and entry.flag in EXCL_FLAGS:
                    continue
                try:
                    yield Markup(get_entry_slice(entry)[0] + "\n")
                except (KeyError, FileNotFoundError):
                    yield Markup(
                        to_string(
                            entry,
                            self.ledger.fava_options.currency_column,
                            indent,
                        ),
                    )


def incomplete_sortkey(entry: Directive) -> tuple[datetime.date, int]:
    """Sortkey for entries that might have incomplete metadata."""
    if isinstance(entry, Open):
        return (entry.date, -2)
    if isinstance(entry, Balance):
        return (entry.date, -1)
    if isinstance(entry, Document):
        return (entry.date, 1)
    if isinstance(entry, Close):
        return (entry.date, 2)
    return (entry.date, 0)


def insert_metadata_in_file(
    path: Path,
    lineno: int,
    indent: int,
    key: str,
    value: str,
) -> None:
    """Insert the specified metadata in the file below lineno.

    Takes the whitespace in front of the line that lineno into account.
    """
    with path.open(encoding="utf-8") as file:
        contents = file.readlines()

    contents.insert(lineno, f'{" " * indent}{key}: "{value}"\n')

    with path.open("w", encoding="utf-8") as file:
        file.write("".join(contents))


def find_entry_lines(lines: list[str], lineno: int) -> list[str]:
    """Lines of entry starting at lineno.

    Args:
        lines: A list of lines.
        lineno: The 0-based line-index to start at.
    """
    entry_lines = [lines[lineno]]
    while True:
        lineno += 1
        try:
            line = lines[lineno]
        except IndexError:
            return entry_lines
        if not line.strip() or re.match(r"\S", line[0]):
            return entry_lines
        entry_lines.append(line)


def get_entry_slice(entry: Directive) -> tuple[str, str]:
    """Get slice of the source file for an entry.

    Args:
        entry: An entry.

    Returns:
        A string containing the lines of the entry and the `sha256sum` of
        these lines.
    """
    path = Path(entry.meta["filename"])
    with path.open(encoding="utf-8") as file:
        lines = file.readlines()

    entry_lines = find_entry_lines(lines, entry.meta["lineno"] - 1)
    entry_source = "".join(entry_lines).rstrip("\n")

    return entry_source, sha256_str(entry_source)


def save_entry_slice(
    entry: Directive,
    source_slice: str,
    sha256sum: str,
) -> str:
    """Save slice of the source file for an entry.

    Args:
        entry: An entry.
        source_slice: The lines that the entry should be replaced with.
        sha256sum: The sha256sum of the current lines of the entry.

    Returns:
        The `sha256sum` of the new lines of the entry.

    Raises:
        FavaAPIError: If the file at `path` is not one of the
            source files.
    """
    path = Path(entry.meta["filename"])
    with path.open(encoding="utf-8") as file:
        lines = file.readlines()

    first_entry_line = entry.meta["lineno"] - 1
    entry_lines = find_entry_lines(lines, first_entry_line)
    entry_source = "".join(entry_lines).rstrip("\n")
    if sha256_str(entry_source) != sha256sum:
        raise ExternallyChangedError(path)

    lines = (
        lines[:first_entry_line]
        + [source_slice + "\n"]
        + lines[first_entry_line + len(entry_lines) :]
    )
    path = Path(entry.meta["filename"])
    with path.open("w", encoding="utf-8") as file:
        file.writelines(lines)

    return sha256_str(source_slice)


def delete_entry_slice(entry: Directive, sha256sum: str) -> None:
    """Delete slice of the source file for an entry.

    Args:
        entry: An entry.
        sha256sum: The sha256sum of the current lines of the entry.

    Raises:
        FavaAPIError: If the file at `path` is not one of the
            source files.
    """
    path = Path(entry.meta["filename"])
    with path.open(encoding="utf-8") as file:
        lines = file.readlines()

    first_entry_line = entry.meta["lineno"] - 1
    entry_lines = find_entry_lines(lines, first_entry_line)
    entry_source = "".join(entry_lines).rstrip("\n")
    if sha256_str(entry_source) != sha256sum:
        raise ExternallyChangedError(path)

    # Also delete the whitespace following this entry
    last_entry_line = first_entry_line + len(entry_lines)
    while True:
        try:
            line = lines[last_entry_line]
        except IndexError:
            break
        if line.strip():
            break
        last_entry_line += 1
    lines = lines[:first_entry_line] + lines[last_entry_line:]
    path = Path(entry.meta["filename"])
    with path.open("w", encoding="utf-8") as file:
        file.writelines(lines)


def insert_entry(
    entry: Directive,
    default_filename: str,
    insert_options: list[InsertEntryOption],
    currency_column: int,
    indent: int,
) -> list[InsertEntryOption]:
    """Insert an entry.

    Args:
        entry: An entry.
        default_filename: The default file to insert into if no option matches.
        insert_options: Insert options.
        currency_column: The column to align currencies at.
        indent: Number of indent spaces.

    Returns:
        A list of updated insert options.
    """
    filename, lineno = find_insert_position(
        entry,
        insert_options,
        default_filename,
    )
    content = to_string(entry, currency_column, indent)

    path = Path(filename)
    with path.open(encoding="utf-8") as file:
        contents = file.readlines()

    if lineno is None:
        # Appending
        contents += "\n" + content
    else:
        contents.insert(lineno, content + "\n")

    with path.open("w", encoding="utf-8") as file:
        file.writelines(contents)

    if lineno is None:
        return insert_options

    added_lines = content.count("\n") + 1
    return [
        (
            replace(option, lineno=option.lineno + added_lines)
            if option.filename == filename and option.lineno > lineno
            else option
        )
        for option in insert_options
    ]


def find_insert_position(
    entry: Directive,
    insert_options: list[InsertEntryOption],
    default_filename: str,
) -> tuple[str, int | None]:
    """Find insert position for an entry.

    Args:
        entry: An entry.
        insert_options: A list of InsertOption.
        default_filename: The default file to insert into if no option matches.

    Returns:
        A tuple of the filename and the line number.
    """
    # Get the list of accounts that should be considered for the entry.
    # For transactions, we want the reversed list of posting accounts.
    accounts = get_entry_accounts(entry)

    # Make no assumptions about the order of insert_options entries and instead
    # sort them ourselves (by descending dates)
    insert_options = sorted(
        insert_options,
        key=attrgetter("date"),
        reverse=True,
    )

    for account in accounts:
        for insert_option in insert_options:
            # Only consider InsertOptions before the entry date.
            if insert_option.date >= entry.date:
                continue
            if insert_option.re.match(account):
                return (insert_option.filename, insert_option.lineno - 1)

    return (default_filename, None)
