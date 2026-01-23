"""Load Beancount files and strings."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.types import LoaderResult

# Environment variable to force beancount backend (for testing/fallback)
_USE_BEANCOUNT = os.environ.get("FAVA_USE_BEANCOUNT", "").lower() in ("1", "true")


def load_string(value: str) -> LoaderResult:
    """Load a Beancount string."""
    if _USE_BEANCOUNT:
        from beancount import loader

        return loader.load_string(value)  # type: ignore[return-value]

    from fava.rustledger.loader import load_string as rl_load_string

    return rl_load_string(value)  # type: ignore[return-value]


def load_uncached(
    beancount_file_path: str,
    *,
    is_encrypted: bool,
) -> LoaderResult:
    """Load a Beancount file."""
    # Encrypted files always use beancount (rustledger doesn't support GPG)
    if is_encrypted or _USE_BEANCOUNT:  # pragma: no cover
        from beancount import loader

        if is_encrypted:
            return loader.load_file(beancount_file_path)  # type: ignore[return-value]

        return loader._load(  # type: ignore[return-value]  # noqa: SLF001
            [(beancount_file_path, True)],
            None,
            None,
            None,
        )

    from fava.rustledger.loader import load_uncached as rl_load_uncached

    return rl_load_uncached(beancount_file_path, is_encrypted=is_encrypted)  # type: ignore[return-value]
