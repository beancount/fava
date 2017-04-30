"""Reading/writing Beancount files."""

import os

from beancount.core import data

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

    def insert_entry(self, entry):
        """Insert an entry.

        Args:
            transaction: An entry.

        """
        insert_entry(entry, self.list_sources(),
                     self.ledger.fava_options['insert-entry'])
        self.ledger.extensions.run_hook('after_insert_entry', entry)


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
    """Insert an entry

    Args:
        entry: An entry.
        filenames: List of filenames.

    """
    if isinstance(entry, data.Transaction):
        accounts = reversed([p.account for p in entry.postings])
    else:
        accounts = entry.account
    filename, lineno = find_insert_position(
        accounts, entry.date, insert_options, filenames)
    content = _render_entry(entry)

    with open(filename, "r") as file:
        contents = file.readlines()

    contents.insert(lineno, content + '\n\n')

    with open(filename, "w") as file:
        file.writelines(contents)


def _render_entry(entry):
    """Render out an entry as string.

    Currently supported are Transaction, Balance and Note.

    Args:
        entry: An entry.

    Returns:
        A string containing the entry in Beancount's format.

    Raises:
        FavaAPIException: If the type of entry is not one of Transaction,
            Balance or Note.
    """
    if isinstance(entry, data.Transaction):
        lines = ['{} {} "{}" "{}"'.format(
            entry.date, entry.flag, entry.payee,
            entry.narration)]

        if entry.meta:
            for key, value in entry.meta.items():
                lines.append('    {}: "{}"'.format(key, value))

        for posting in entry.postings:
            line = '    {}'.format(posting.account)
            if posting.units:
                number_length = str(posting.units.number).find('.')
                line += ' ' * max(49 - len(posting.account) - number_length, 2)
                line += '{} {}'.format(posting.units.number or '',
                                       posting.units.currency or '')
            lines.append(line)

        return '\n'.join(lines)

    if isinstance(entry, data.Balance):
        return '{} balance {} {} {}'.format(
            entry.date, entry.account, entry.amount.number,
            entry.amount.currency)

    if isinstance(entry, data.Note):
        return '{} note {} "{}"'.format(
            entry.date, entry.account, entry.comment)

    raise FavaAPIException(
        'Rendering entries of type {} is not implemented.'.format(
            entry.__class__.__name__))


def find_insert_position(accounts, date, insert_options, filenames):
    """Find insert position for an account.

    Args:
        accounts: An account name (str) or a iterable of accounts.
        date: A date. Only InsertOptions before this date will be considered.
        insert_options: A list of InsertOption.
        filenames: List of Beancount files.
    """
    position = None
    if isinstance(accounts, str):
        accounts = [accounts]

    for account in accounts:
        for insert_option in insert_options:
            if insert_option.date >= date:
                break
            if insert_option.re.match(account):
                position = (insert_option.filename, insert_option.lineno-1)

    if not position:
        position = filenames[0], len(open(filenames[0]).readlines())+1

    return position
