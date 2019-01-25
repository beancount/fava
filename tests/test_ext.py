# pylint: disable=missing-docstring

import os

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

    path = os.path.join(os.path.dirname(__file__), "../fava/ext")
    classes, errors = find_extensions(path, "auto_commit")
    assert len(classes) == 1
    assert classes[0].__name__ == "AutoCommit"
    assert errors == []

    path = os.path.join(os.path.dirname(__file__), "../fava/ext")
    classes, errors = find_extensions(path, "portfolio_list")
    assert len(classes) == 1
    assert classes[0].__name__ == "PortfolioList"
    assert errors == []
