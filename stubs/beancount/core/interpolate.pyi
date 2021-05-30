# pylint: disable=missing-docstring,unused-argument,multiple-statements

from typing import Any
from typing import Tuple

from beancount.core.data import Entries
from beancount.core.data import Directive

def compute_entry_context(
    entries: Entries, context_entry: Directive
) -> Tuple[Any, Any]: ...
