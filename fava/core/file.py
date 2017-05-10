"""Reading/writing Beancount files."""

import os

from beancount.core import data
from beancount.parser.printer import format_entry

from fava.core.helpers import FavaAPIException, FavaModule


class FileModule(FavaModule):
    """Functions related to reading/writing to Beancount files."""

    def list_sources(self):
        """List source files.

        Returns:
            A list of all sources files, with the main file listed first.

        """
        main_file = self.ledger.beancount_file_path
        return [main_file] + \
            sorted(filter(
                lambda x: x != main_file,
                [os.path.join(
                    os.path.dirname(main_file), filename)
                 for filename in self.ledger.options['include']]))

    def get_source(self, path):
        """Get source files.

        Args:
            path: The path of the file.

        Returns:
            A string with the file contents.

        Raises:
            FavaAPIException: If the file at `path` is not one of the
                source files.

        """
        if path not in self.list_sources():
            raise FavaAPIException('Trying to read a non-source file')

        with open(path, encoding='utf8') as file:
            source = file.read()
        return source

    def set_source(self, path, source):
        """Write to source file.

        Args:
            path: The path of the file.
            source: A string with the file contents.

        Raises:
            FavaAPIException: If the file at `path` is not one of the
                source files.

        """
        if path not in self.list_sources():
            raise FavaAPIException('Trying to write a non-source file')

        with open(path, 'w+', encoding='utf8') as file:
            file.write(source)
        self.ledger.extensions.run_hook('after_write_source', path, source)
        self.load_file()

    def insert_metadata(self, entry_hash, basekey, value):
        """Insert metadata into a file at lineno.

        Also, prevent duplicate keys.
        """
        self.ledger.changed()
        entry = self.ledger.get_entry(entry_hash)
        key = next_key(basekey, entry.meta)
        insert_metadata_in_file(entry.meta['filename'],
                                entry.meta['lineno'] - 1, key, value)
        self.ledger.extensions.run_hook('after_insert_metadata', entry, key,
                                        value)

    def insert_entries(self, entries):
        """Insert entries.

        Args:
            entries: A list of entries.

        """
        self.ledger.changed()
        for entry in sorted(entries, key=incomplete_sortkey):
            insert_entry(entry,
                         self.list_sources(),
                         self.ledger.fava_options['insert-entry'])
            self.ledger.extensions.run_hook('after_insert_entry', entry)


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
    while '{}-{}'.format(basekey, i) in keys:
        i = i + 1
    return '{}-{}'.format(basekey, i)


def leading_space(line):
    """Returns a string representing the leading whitespace for the specified
    string."""
    return line[:len(line) - len(line.lstrip())]


def insert_metadata_in_file(filename, lineno, key, value):
    """Inserts the specified metadata in the file below lineno, taking into
    account the whitespace in front of the line that lineno."""
    with open(filename, "r") as file:
        contents = file.readlines()

    # use the whitespace of the following line, else use double the whitespace
    indention = leading_space(contents[lineno + 1])

    contents.insert(lineno + 1, '{}{}: "{}"\n'.format(indention, key, value))

    with open(filename, "w") as file:
        contents = "".join(contents)
        file.write(contents)


def insert_entry(entry, filenames, insert_options):
    """Insert an entry.

    Args:
        entry: An entry.
        filenames: List of filenames.
        insert_options: List of InsertOption. Note that the line numbers of the
            options might be updated.

    """
    if isinstance(entry, data.Transaction):
        accounts = reversed([p.account for p in entry.postings])
    else:
        accounts = [entry.account]
    filename, lineno = find_insert_position(accounts, entry.date,
                                            insert_options, filenames)
    content = _format_entry(entry) + '\n'

    with open(filename, "r") as file:
        contents = file.readlines()

    contents.insert(lineno, content)

    with open(filename, "w") as file:
        file.writelines(contents)

    for index, option in enumerate(insert_options):
        if option.filename == filename and option.lineno > lineno:
            insert_options[index] = option._replace(
                lineno=lineno + content.count('\n') + 1)


def _format_entry(entry):
    """Wrapper that strips unnecessary whitespace from format_entry."""
    string = format_entry(entry)
    return '\n'.join((line.rstrip() for line in string.split('\n')))


def find_insert_position(accounts, date, insert_options, filenames):
    """Find insert position for an account.

    Args:
        accounts: A list of accounts.
        date: A date. Only InsertOptions before this date will be considered.
        insert_options: A list of InsertOption.
        filenames: List of Beancount files.
    """
    position = None

    for account in accounts:
        for insert_option in insert_options:
            if insert_option.date >= date:
                break
            if insert_option.re.match(account):
                position = (insert_option.filename, insert_option.lineno - 1)

    if not position:
        position = filenames[0], len(open(filenames[0]).readlines()) + 1

    return position
