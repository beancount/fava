"""Rustledger WASM integration for Fava.

This module provides a Python interface to rustledger via wasmtime-py,
replacing beancount for parsing, validation, and querying.
"""

from __future__ import annotations

from fava.rustledger.engine import RustledgerEngine
from fava.rustledger.loader import load_string
from fava.rustledger.loader import load_uncached

__all__ = [
    "RustledgerEngine",
    "load_string",
    "load_uncached",
]
