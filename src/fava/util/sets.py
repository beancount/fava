"""Utils for Python sets."""
from typing import AbstractSet
from typing import Optional
from typing import Set


def add_to_set(set_: Optional[AbstractSet[str]], new: str) -> Set[str]:
    """Add an entry to a set (or create it if doesn't exist).

    Args:
        set_: The (optional) set to add an element to.
        new: The string to add to the set.
    """
    return set(set_).union([new]) if set_ is not None else {new}
