"""Load Beancount files and strings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from beancount import loader

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.types import LoaderResult


def load_string(value: str) -> LoaderResult:
    """Load a Beancoun string."""
    return loader.load_string(value)


def load_uncached(
    beancount_file_path: str,
    *,
    is_encrypted: bool,
) -> LoaderResult:
    """Load a Beancount file."""
    if is_encrypted:  # pragma: no cover
        return loader.load_file(beancount_file_path)

    return loader._load(  # type: ignore[attr-defined,no-any-return]  # noqa: SLF001
        [(beancount_file_path, True)],
        None,
        None,
        None,
    )
