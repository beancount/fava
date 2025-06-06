from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from fava.ext import ExtensionConfigError
from fava.ext import find_extensions
from fava.ext.portfolio_list import PortfolioList

if TYPE_CHECKING:
    from fava.core import FavaLedger


def test_extension_load_config(small_example_ledger: FavaLedger) -> None:
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

    classes, errors = find_extensions(Path(), "fava")
    assert not classes
    assert len(errors) == 1
    assert errors[0].message == 'Module "fava" contains no extensions.'

    path = Path(__file__).parent.parent / "src" / "fava" / "ext"
    classes, errors = find_extensions(path, "auto_commit")
    assert len(classes) == 1
    assert classes[0].__name__ == "AutoCommit"
    assert not errors

    path = Path(__file__).parent.parent / "src" / "fava" / "ext"
    classes, errors = find_extensions(path, "portfolio_list")
    assert len(classes) == 1
    assert classes[0].__name__ == "PortfolioList"
    assert not errors
