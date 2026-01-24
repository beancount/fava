from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from rustfava.ext import ExtensionConfigError
from rustfava.ext import find_extensions
from rustfava.ext.portfolio_list import PortfolioList

if TYPE_CHECKING:
    from rustfava.core import RustfavaLedger


def test_extension_load_config(small_example_ledger: RustfavaLedger) -> None:
    PortfolioList(small_example_ledger)

    with pytest.raises(ExtensionConfigError):
        PortfolioList(small_example_ledger, "{{")


def test_find_extensions() -> None:
    classes, errors = find_extensions(Path(), "NOMODULENAME")
    assert not classes
    assert len(errors) == 1
    assert (
        errors[0].message == 'Importing module "NOMODULENAME" failed.'
        "\nError: \"No module named 'NOMODULENAME'\""
    )

    classes, errors = find_extensions(Path(), "rustfava")
    assert not classes
    assert len(errors) == 1
    assert errors[0].message == 'Module "rustfava" contains no extensions.'

    path = Path(__file__).parent.parent / "src" / "rustfava" / "ext"
    classes, errors = find_extensions(path, "auto_commit")
    assert len(classes) == 1
    assert classes[0].__name__ == "AutoCommit"
    assert not errors

    path = Path(__file__).parent.parent / "src" / "rustfava" / "ext"
    classes, errors = find_extensions(path, "portfolio_list")
    assert len(classes) == 1
    assert classes[0].__name__ == "PortfolioList"
    assert not errors
