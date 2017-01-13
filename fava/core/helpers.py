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
    def __init__(self, ledger):
        self.ledger = ledger

    def load_file(self):
        pass
