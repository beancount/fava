"""Type checking helper for unreachable code."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from typing import Never


class UnreachableCodeAssertionError(AssertionError):
    """Expected code to be unreachable."""

    def __init__(self) -> None:  # pragma: no cover
        super().__init__("Expected code to be unreachable")


def assert_never(_: Never) -> Never:  # pragma: no cover
    """Assert that this code is unreachable."""
    raise UnreachableCodeAssertionError
