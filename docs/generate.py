"""Generate the reST-files for the API documentation.

sphinx-apidoc is not customizeable enough to do this.
"""

from __future__ import annotations

import pkgutil
from pathlib import Path

import fava

MODULES = list(pkgutil.walk_packages(fava.__path__, fava.__name__ + "."))

RST_PATH = Path(__file__).parent / "api"
if not RST_PATH.is_dir():
    RST_PATH.mkdir()


def heading(name: str, level: str = "-") -> str:
    """Return the rst-heading for the given heading."""
    return f"{name}\n{level * len(name)}\n\n"


for package in ["fava"] + [mod.name for mod in MODULES if mod.ispkg]:
    submodules = [
        mod.name
        for mod in MODULES
        if mod.name.startswith(package)
        and not mod.ispkg
        and "_test" not in mod.name
        and mod.name.count(".") == package.count(".") + 1
    ]
    with (RST_PATH / f"{package}.rst").open("w") as rst:
        rst.write(heading(package, "="))
        rst.write(f".. automodule:: {package}\n\n")
        for submod in submodules:
            rst.write(heading(submod, "-"))
            rst.write(f".. automodule:: {submod}\n\n")
