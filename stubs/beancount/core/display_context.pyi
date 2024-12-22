import enum

class Precision(enum.Enum):
    MOST_COMMON = 1
    MAXIMUM = 2

class _CurrencyContext:
    has_sign: bool = ...
    def get_fractional(self, precision: Precision) -> int | None: ...

class DisplayContext:
    ccontexts: dict[str, _CurrencyContext] = ...
