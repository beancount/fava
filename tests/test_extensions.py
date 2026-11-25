"""Tests for the extension system."""

from __future__ import annotations

import os
import sys
import textwrap
from typing import TYPE_CHECKING

from fava.core import FavaLedger
from fava.core.extensions import ExtensionDetails
from fava.ext import find_extensions

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path

    from .conftest import GetFavaLedger


def test_report_page_globals(get_ledger: GetFavaLedger) -> None:
    """Extensions can register reports and have JS modules."""
    extension_report_ledger = get_ledger("extension-report")
    result = extension_report_ledger.extensions.extension_details
    assert result == [
        ExtensionDetails(
            "FavaExtTest",
            "Fava extension test",
            has_js_module=True,
        ),
    ]
    extension_report_ledger.load_file()
    assert result == [
        ExtensionDetails(
            "FavaExtTest",
            "Fava extension test",
            has_js_module=True,
        ),
    ]

    extension_report_ledger.extensions.after_write_source("test", "test")

    ext = extension_report_ledger.extensions.get_extension("FavaExtTest")
    assert ext
    assert ext.name == "FavaExtTest"

    assert ext.extension_dir.exists()
    assert (ext.extension_dir / "FavaExtTest.js").exists()


def test_force_reload_reimports_extension(tmp_path: Path) -> None:
    """force_reload reimports extension modules so source changes apply."""
    module_name = "fava_force_reload_ext"
    module_path = tmp_path / f"{module_name}.py"
    module_path.write_text(
        textwrap.dedent(
            """\
            from fava.ext import FavaExtensionBase

            class ForceReloadExt(FavaExtensionBase):
                report_title = "v1"
            """
        ),
        encoding="utf-8",
    )
    ledger_path = tmp_path / "ledger.beancount"
    ledger_path.write_text(
        textwrap.dedent(
            f"""\
            option "title" "Force Reload"
            2010-01-01 custom "fava-extension" "{module_name}"
            2010-01-01 open Assets:Cash
            """
        ),
        encoding="utf-8",
    )

    try:
        ledger = FavaLedger(str(ledger_path))
        ext = ledger.extensions.get_extension("ForceReloadExt")
        assert ext is not None
        assert ext.report_title == "v1"
        first_id = id(ext)

        # Different-length title so size changes; bump mtime past second
        # resolution so a same-second rewrite cannot keep a stale .pyc.
        module_path.write_text(
            textwrap.dedent(
                """\
                from fava.ext import FavaExtensionBase

                class ForceReloadExt(FavaExtensionBase):
                    report_title = "v2-reloaded"
                """
            ),
            encoding="utf-8",
        )
        new_mtime = module_path.stat().st_mtime + 2.0
        os.utime(module_path, (new_mtime, new_mtime))

        # A normal load keeps the previously imported extension instance.
        ledger.load_file()
        ext_after_load = ledger.extensions.get_extension("ForceReloadExt")
        assert ext_after_load is not None
        assert ext_after_load.report_title == "v1"
        assert id(ext_after_load) == first_id

        ledger.force_reload()
        ext_after_force = ledger.extensions.get_extension("ForceReloadExt")
        assert ext_after_force is not None
        assert ext_after_force.report_title == "v2-reloaded"
        assert id(ext_after_force) != first_id
    finally:
        sys.modules.pop(module_name, None)


def test_force_reload_with_plugins(get_ledger: GetFavaLedger) -> None:
    """force_reload also drops Beancount plugin modules when present."""
    ledger = get_ledger("example")
    assert ledger.options.get("plugin")
    ledger.force_reload()
    assert ledger.extensions.errors == []


def test_find_extensions_reload(tmp_path: Path) -> None:
    """find_extensions can reload an already imported module."""
    module_name = "fava_find_ext_reload"
    module_path = tmp_path / f"{module_name}.py"
    module_path.write_text(
        textwrap.dedent(
            """\
            from fava.ext import FavaExtensionBase

            class FindExt(FavaExtensionBase):
                report_title = "before"
            """
        ),
        encoding="utf-8",
    )

    try:
        classes, errors = find_extensions(tmp_path, module_name)
        assert not errors
        assert classes[0].report_title == "before"

        module_path.write_text(
            textwrap.dedent(
                """\
                from fava.ext import FavaExtensionBase

                class FindExt(FavaExtensionBase):
                    report_title = "after"
                """
            ),
            encoding="utf-8",
        )

        classes_cached, _ = find_extensions(tmp_path, module_name)
        assert classes_cached[0].report_title == "before"

        classes_reloaded, _ = find_extensions(
            tmp_path, module_name, reload=True
        )
        assert classes_reloaded[0].report_title == "after"
    finally:
        sys.modules.pop(module_name, None)
