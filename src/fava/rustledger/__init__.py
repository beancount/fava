"""Rustledger WASM integration for Fava.

This module provides a Python interface to rustledger via wasmtime-py,
replacing beancount for parsing, validation, and querying.
"""

from __future__ import annotations

from fava.rustledger.engine import RustledgerEngine
from fava.rustledger.loader import load_string
from fava.rustledger.loader import load_uncached


def is_encrypted_file(path: str) -> bool:
    """Check if a file is GPG encrypted.

    Args:
        path: Path to file

    Returns:
        True if file is encrypted
    """
    return RustledgerEngine.get_instance().is_encrypted(path)


__all__ = [
    "RustledgerEngine",
    "is_encrypted_file",
    "load_string",
    "load_uncached",
]
