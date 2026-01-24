"""Tests for the extension system."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rustfava.core.extensions import ExtensionDetails

if TYPE_CHECKING:  # pragma: no cover
    from .conftest import GetRustfavaLedger


def test_report_page_globals(get_ledger: GetRustfavaLedger) -> None:
    """Extensions can register reports and have JS modules."""
    extension_report_ledger = get_ledger("extension-report")
    result = extension_report_ledger.extensions.extension_details
    assert result == [
        ExtensionDetails(
            "RustfavaExtTest",
            "Rustfava extension test",
            has_js_module=True,
        ),
    ]
    extension_report_ledger.load_file()
    assert result == [
        ExtensionDetails(
            "RustfavaExtTest",
            "Rustfava extension test",
            has_js_module=True,
        ),
    ]

    extension_report_ledger.extensions.after_write_source("test", "test")

    ext = extension_report_ledger.extensions.get_extension("RustfavaExtTest")
    assert ext
    assert ext.name == "RustfavaExtTest"

    assert ext.extension_dir.exists()
    assert (ext.extension_dir / "RustfavaExtTest.js").exists()
