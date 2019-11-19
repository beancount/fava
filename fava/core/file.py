"""Reading/writing Beancount files."""

import codecs
from hashlib import sha256
import os
import re

from beancount.core import data, flags
from beancount.parser.printer import format_entry

from fava.core.helpers import FavaAPIException, FavaModule
from fava.core.misc import align


class FileModule(FavaModule):
    """Functions related to reading/writing to Beancount files."""

    def list_sources(self):
        """List source files.

        Returns:
            A list of all sources files, with the main file listed first.

        """
        main_file = self.ledger.beancount_file_path
        return [main_file] + sorted(
            filter(
                lambda x: x != main_file,
                [
                    os.path.join(os.path.dirname(main_file), filename)
                    for filename in self.ledger.options["include"]
                ],
            )
        )

    def get_source(self, path):
        """Get source files.

        Args:
            path: The path of the file.

        Returns:
            A string with the file contents and the `sha256sum` of the file.

        Raises:
            FavaAPIException: If the file at `path` is not one of the
                source files.

        """
        if path not in self.list_sources():
            raise FavaAPIException("Trying to read a non-source file")

        with open(path, mode="rb") as file:
            contents = file.read()

        sha256sum = sha256(contents).hexdigest()
        source = codecs.decode(contents)

        return source, sha256sum

    def set_source(self, path, source, sha256sum):
        """Write to source file.

        Args:
            path: The path of the file.
            source: A string with the file contents.
            sha256sum: Hash of the file.

        Returns:
            The `sha256sum` of the updated file.

        Raises:
            FavaAPIException: If the file at `path` is not one of the
                source files or if the file was changed externally.

        """
        _, original_sha256sum = self.get_source(path)
        if original_sha256sum != sha256sum:
            raise FavaAPIException("The file changed externally.")

        contents = codecs.encode(source)
        with open(path, "w+b") as file:
            file.write(contents)

        self.ledger.extensions.run_hook("after_write_source", path, source)
        self.ledger.load_file()

        return sha256(contents).hexdigest()

    def insert_metadata(self, entry_hash, basekey, value):
        """Insert metadata into a file at lineno.

        Also, prevent duplicate keys.
        """
        self.ledger.changed()
        entry = self.ledger.get_entry(entry_hash)
        key = next_key(basekey, entry.meta)
        insert_metadata_in_file(
            entry.meta["filename"], entry.meta["lineno"] - 1, key, value
        )
        self.ledger.extensions.run_hook(
            "after_insert_metadata", entry, key, value
        )

    def insert_entries(self, entries):
        """Insert entries.

        Args:
            entries: A list of entries.

        """
        self.ledger.changed()
        for entry in sorted(entries, key=incomplete_sortkey):
            insert_entry(entry, self.list_sources(), self.ledger.fava_options)
            self.ledger.extensions.run_hook("after_insert_entry", entry)

    def render_entries(self, entries):
        """Return entries in Beancount format.

        Only renders :class:`.Balance` and :class:`.Transaction`.

        Args:
            entries: A list of entries.

        Yields:
            The entries rendered in Beancount format.

        """
        excl_flags = [
            flags.FLAG_PADDING,  # P
            flags.FLAG_SUMMARIZE,  # S
            flags.FLAG_TRANSFER,  # T
            flags.FLAG_CONVERSIONS,  # C
            flags.FLAG_UNREALIZED,  # U
            flags.FLAG_RETURNS,  # R
            flags.FLAG_MERGING,  # M
        ]

        for entry in entries:
            if isinstance(entry, (data.Balance, data.Transaction)):
                if (
                    isinstance(entry, data.Transaction)
                    and entry.flag in excl_flags
                ):
                    continue
                try:
                    yield get_entry_slice(entry)[0] + "\n"
                except FileNotFoundError:
                    yield _format_entry(entry, self.ledger.fava_options)


def incomplete_sortkey(entry):
    """Sortkey for entries that might have incomplete metadata."""
    return (entry.date, data.SORT_ORDER.get(type(entry), 0))


def next_key(basekey, keys):
    """Returns the next unused key for basekey in the supplied array.

    The first try is `basekey`, followed by `basekey-2`, `basekey-3`, etc
    until a free one is found.
    """
    if basekey not in keys:
        return basekey
    i = 2
    while "{}-{}".format(basekey, i) in keys:
        i = i + 1
    return "{}-{}".format(basekey, i)


def leading_space(line):
    """Returns a string representing the leading whitespace for the specified
    string."""
    return line[: len(line) - len(line.lstrip())]


def insert_metadata_in_file(filename, lineno, key, value):
    """Inserts the specified metadata in the file below lineno, taking into
    account the whitespace in front of the line that lineno."""
    with open(filename, "r", encoding="utf-8") as file:
        contents = file.readlines()

    # use the whitespace of the following line, else use double the whitespace
    indention = leading_space(contents[lineno + 1])

    contents.insert(lineno + 1, '{}{}: "{}"\n'.format(indention, key, value))

    with open(filename, "w", encoding="utf-8") as file:
        contents = "".join(contents)
        file.write(contents)


def find_entry_lines(lines, lineno):
    """Lines of entry starting at lineno."""
    entry_lines = [lines[lineno]]
    while True:
        lineno += 1
        try:
            line = lines[lineno]
        except IndexError:
            break
        if not line.strip() or re.match("[0-9a-z]", line[0]):
            break
        entry_lines.append(line)
    return entry_lines


def get_entry_slice(entry):
    """Get slice of the source file for an entry.

    Args:
        entry: An entry.

    Returns:
        A string containing the lines of the entry and the `sha256sum` of
        these lines.

    Raises:
        FavaAPIException: If the file at `path` is not one of the
            source files.

    """
    with open(entry.meta["filename"], mode="r", encoding="utf-8") as file:
        lines = file.readlines()

    entry_lines = find_entry_lines(lines, entry.meta["lineno"] - 1)
    entry_source = "".join(entry_lines).rstrip("\n")
    sha256sum = sha256(codecs.encode(entry_source)).hexdigest()

    return entry_source, sha256sum


def save_entry_slice(entry, source_slice, sha256sum):
    """Save slice of the source file for an entry.

    Args:
        entry: An entry.
        source_slice: The lines that the entry should be replaced with.
        sha256sum: The sha256sum of the current lines of the entry.

    Returns:
        The `sha256sum` of the new lines of the entry.

    Raises:
        FavaAPIException: If the file at `path` is not one of the
            source files.

    """

    with open(entry.meta["filename"], "r", encoding="utf-8") as file:
        lines = file.readlines()

    first_entry_line = entry.meta["lineno"] - 1
    entry_lines = find_entry_lines(lines, first_entry_line)
    entry_source = "".join(entry_lines).rstrip("\n")
    original_sha256sum = sha256(codecs.encode(entry_source)).hexdigest()
    if original_sha256sum != sha256sum:
        raise FavaAPIException("The file changed externally.")

    lines = (
        lines[:first_entry_line]
        + [source_slice + "\n"]
        + lines[first_entry_line + len(entry_lines) :]
    )
    with open(entry.meta["filename"], "w", encoding="utf-8") as file:
        file.writelines(lines)

    return sha256(codecs.encode(source_slice)).hexdigest()


def insert_entry(entry, filenames, fava_options):
    """Insert an entry.

    Args:
        entry: An entry.
        filenames: List of filenames.
        fava_options: The ledgers fava_options. Note that the line numbers of
            the insert options might be updated.
    """
    insert_options = fava_options.get("insert-entry", [])
    if isinstance(entry, data.Transaction):
        accounts = reversed([p.account for p in entry.postings])
    else:
        accounts = [entry.account]
    filename, lineno = find_insert_position(
        accounts, entry.date, insert_options, filenames
    )
    content = _format_entry(entry, fava_options) + "\n"

    with open(filename, "r", encoding="utf-8") as file:
        contents = file.readlines()

    contents.insert(lineno, content)

    with open(filename, "w", encoding="utf-8") as file:
        file.writelines(contents)

    for index, option in enumerate(insert_options):
        added_lines = content.count("\n") + 1
        if option.filename == filename and option.lineno > lineno:
            insert_options[index] = option._replace(
                lineno=lineno + added_lines
            )


def _format_entry(entry, fava_options):
    """Wrapper that strips unnecessary whitespace from format_entry."""
    meta = {
        key: entry.meta[key] for key in entry.meta if not key.startswith("_")
    }
    entry = entry._replace(meta=meta)
    string = align(format_entry(entry), fava_options)
    string = string.replace("<class 'beancount.core.number.MISSING'>", "")
    return "\n".join((line.rstrip() for line in string.split("\n")))


def find_insert_position(accounts, date, insert_options, filenames):
    """Find insert position for an account.

    Args:
        accounts: A list of accounts.
        date: A date. Only InsertOptions before this date will be considered.
        insert_options: A list of InsertOption.
        filenames: List of Beancount files.

    Returns:
        A tuple of the filename and the line number.
    """
    # Make no assumptions about the order of insert_options entries and instead
    # sort them ourselves (by descending dates)
    sorted_insert_options = sorted(
        insert_options, key=lambda x: x.date, reverse=True
    )
    for account in accounts:
        for insert_option in sorted_insert_options:
            if insert_option.date >= date:
                continue
            if insert_option.re.match(account):
                return (insert_option.filename, insert_option.lineno - 1)

    return (
        filenames[0],
        len(open(filenames[0], encoding="utf-8").readlines()) + 1,
    )
