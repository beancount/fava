# pylint: disable=missing-docstring,unused-argument,multiple-statements
import datetime

from fava.beans.abc import Directive

def get_min_max_dates(
    entries: list[Directive], types: type | tuple[type, ...] | None = ...
) -> tuple[None, None] | tuple[datetime.date, datetime.date]: ...
