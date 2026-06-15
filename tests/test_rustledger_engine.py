"""Tests for rustledger FFI api_version validation.

Regression coverage for https://github.com/rustledger/rustfava/issues/159 —
the engine previously declared a supported-version constant but never read or
enforced ``api_version``, so any (incompatible) server version was accepted
silently.
"""

from __future__ import annotations

import pytest

from rustfava.rustledger.engine import _check_api_version
from rustfava.rustledger.engine import RustledgerAPIVersionError
from rustfava.rustledger.engine import SUPPORTED_API_MAJOR


@pytest.mark.parametrize(
    "version",
    [
        None,  # responses without api_version are not checked
        f"{SUPPORTED_API_MAJOR}.0",
        f"{SUPPORTED_API_MAJOR}.1",  # higher minor is additive/back-compatible
        f"{SUPPORTED_API_MAJOR}.10",
        str(SUPPORTED_API_MAJOR),  # bare major
    ],
)
def test_check_api_version_accepts_compatible(version: str | None) -> None:
    # Must not raise.
    _check_api_version(version)


@pytest.mark.parametrize(
    "version",
    [
        f"{SUPPORTED_API_MAJOR - 1}.0",  # older major
        f"{SUPPORTED_API_MAJOR + 1}.0",  # newer major
        "not-a-version",  # unparseable
    ],
)
def test_check_api_version_rejects_incompatible(version: str) -> None:
    with pytest.raises(RustledgerAPIVersionError):
        _check_api_version(version)
