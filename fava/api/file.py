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
