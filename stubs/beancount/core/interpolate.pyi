# pylint: disable=missing-docstring,unused-argument,multiple-statements
from typing import Any

from beancount.core.data import Directive
from beancount.core.data import Entries

def compute_entry_context(
    entries: Entries, context_entry: Directive
) -> tuple[Any, Any]: ...
