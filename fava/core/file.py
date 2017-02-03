"""Reading/writing Beancount files."""

import os

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
        entry = self.ledger.get_entry(entry_hash)
        key = next_key(basekey, entry.meta)
        insert_metadata_in_file(entry.meta['filename'], entry.meta['lineno']-1,
                                key, value)
        self.ledger.extensions.run_hook('after_insert_metadata', entry, key,
                                        value)

    def insert_transaction(self, transaction):
        """Insert a transaction.

        Args:
            transaction: A Transaction.

        """
        insert_transaction(transaction, self.list_sources())
        self.ledger.extensions.run_hook('after_insert_transaction',
                                        transaction)


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


def insert_transaction(transaction, filenames):
    """Insert a transaction.

    Args:
        transaction: A Transaction.
        filenames: List of filenames.

    """
    filename, lineno = find_insert_marker(filenames)
    content = _render_transaction(transaction)

    with open(filename, "r") as file:
        contents = file.readlines()

    contents.insert(lineno, '\n' + content + '\n')

    with open(filename, "w") as file:
        file.writelines(contents)


def _render_transaction(transaction):
    """Render out a transaction as string.

    Args:
        transaction: A Transaction.

    Returns:
        A string containing the transaction in Beancount's format.

    """
    lines = ['{} {} "{}" "{}"'.format(
        transaction.date, transaction.flag, transaction.payee,
        transaction.narration)]

    if transaction.meta and len(transaction.meta.keys()) > 0:
        for key, value in transaction.meta.items():
            lines.append('    {}: "{}"'.format(key, value))

    for posting in transaction.postings:
        line = '    {}'.format(posting.account)
        if posting.units.number or posting.units.currency:
            number_length = str(posting.units.number).find('.')
            line += ' ' * max(49 - len(posting.account) - number_length, 2)
            line += '{} {}'.format(posting.units.number or '',
                                   posting.units.currency or '')
        lines.append(line)

    return '\n'.join(lines)


def find_insert_marker(filenames):
    """Searches for the insert marker and returns (filename, lineno).
    Defaults to the first file and last line if not found.
    """
    marker = 'FAVA-INSERT-MARKER'

    for filename in filenames:
        with open(filename, "r") as file:
            for lineno, linetext in enumerate(file):
                if marker in linetext:
                    return filename, lineno

    return filenames[0], len(open(filenames[0]).readlines())+1
