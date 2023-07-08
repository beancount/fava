"""Load Beancount files and strings."""

from __future__ import annotations

from typing import TYPE_CHECKING

import uromyces
from beancount import loader
from uromyces._convert import convert_options

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.types import LoaderResult


def load_string(value: str) -> LoaderResult:
    """Load a Beancoun string."""
    return loader.load_string(value)  # type: ignore[return-value]


def load_uncached(
    beancount_file_path: str,
    *,
    is_encrypted: bool,
    use_uromyces: bool,
) -> LoaderResult:
    """Load a Beancount file."""
    if is_encrypted:  # pragma: no cover
        return loader.load_file(beancount_file_path)  # type: ignore[return-value]

    if use_uromyces:
        ledger = uromyces.load_file(beancount_file_path)
        return (  # type: ignore[return-value]
            ledger.entries,
            ledger.errors,
            convert_options(ledger),
        )
    return loader._load(  # type: ignore[return-value]  # noqa: SLF001
        [(beancount_file_path, True)],
        None,
        None,
        None,
    )
