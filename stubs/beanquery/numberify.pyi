from collections.abc import Sequence
from typing import Any

from beanquery import Column

def numberify_results(
    rtypes: Sequence[Column],
    rrows: Sequence[tuple[Any, ...]],
    dcontext: Any,
) -> tuple[list[Column], list[tuple[Any, ...]]]: ...
