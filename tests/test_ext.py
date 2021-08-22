# pylint: disable=missing-docstring
from pathlib import Path

from fava.ext import find_extensions


def test_find_extensions():
    classes, errors = find_extensions(".", "NOMODULENAME")
    assert classes == []
    assert len(errors) == 1
    assert errors[0].message == 'Importing module "NOMODULENAME" failed.'

    classes, errors = find_extensions(".", "fava")
    assert classes == []
    assert len(errors) == 1
    assert errors[0].message == 'Module "fava" contains no extensions.'

    path = Path(__file__).parent.parent / "src" / "fava" / "ext"
    classes, errors = find_extensions(str(path), "auto_commit")
    assert len(classes) == 1
    assert classes[0].__name__ == "AutoCommit"
    assert errors == []

    path = Path(__file__).parent.parent / "src" / "fava" / "ext"
    classes, errors = find_extensions(str(path), "portfolio_list")
    assert len(classes) == 1
    assert classes[0].__name__ == "PortfolioList"
    assert errors == []
