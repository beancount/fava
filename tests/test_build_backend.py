from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

from setuptools import build_meta


def test_build_backend_has_all_hooks() -> None:
    dir_ = Path(__file__).parent
    sys.path.insert(0, str(dir_))
    build_backend = import_module("_build_backend")
    sys.path.pop(0)
    build_meta_all = set(build_meta.__all__)
    build_meta_all.remove("__legacy__")
    build_meta_all.remove("SetupRequirementsError")
    assert build_meta_all == set(build_backend.__all__)
