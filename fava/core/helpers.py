class FavaAPIException(Exception):
    """Fava's base exception class."""

    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message


class FilterException(FavaAPIException):
    """Filter exception."""

    def __init__(self, filter_type, message):
        super().__init__(message)
        self.filter_type = filter_type

    def __str__(self):
        return self.message


class FavaModule(object):
    def __init__(self, api):
        self.api = api

    def load_file(self):
        pass


def entry_at_lineno(entries, filename, lineno):
    """Returns the entry in filename at lineno."""
    for entry in entries:
        if entry.meta['filename'] == filename and \
           entry.meta['lineno'] == lineno:
            return entry

    raise FavaAPIException('No entry in file {} at line {}'.format(
        filename, lineno))
