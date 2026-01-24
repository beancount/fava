"""Load Beancount files and strings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fava.rustledger.loader import load_string as rl_load_string
from fava.rustledger.loader import load_uncached as rl_load_uncached

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.types import LoaderResult


def load_string(value: str) -> LoaderResult:
    """Load a Beancount string."""
    return rl_load_string(value)  # type: ignore[return-value]


def load_uncached(
    beancount_file_path: str,
    *,
    is_encrypted: bool,
) -> LoaderResult:
    """Load a Beancount file."""
    # Encrypted files use beancount (rustledger doesn't support GPG decryption)
    if is_encrypted:  # pragma: no cover
        from beancount import loader

        return loader.load_file(beancount_file_path)  # type: ignore[return-value]

    return rl_load_uncached(beancount_file_path, is_encrypted=is_encrypted)  # type: ignore[return-value]
