# pylint: disable=missing-docstring,unused-argument,multiple-statements
from typing import Any
from typing import Optional

def bisect_left_with_key(
    sequence: Any, value: Any, key: Optional[Any] = ...
): ...
def bisect_right_with_key(
    sequence: Any,
    value: Any,
    key: Any,
    low_idx: int = ...,
    high_idx: Optional[Any] = ...,
): ...
