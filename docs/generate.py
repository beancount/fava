"""Generate the reST-files for the API documentation.

sphinx-apidoc is not customizeable enough to do this.
"""
import os
import pkgutil
from os import path

import fava

MODULES = list(pkgutil.walk_packages(fava.__path__, fava.__name__ + "."))

RST_PATH = path.join(path.dirname(__file__), "api")
if not path.isdir(RST_PATH):
    os.mkdir(RST_PATH)


def heading(name, level="-"):
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
    with open(path.join(RST_PATH, f"{package}.rst"), "w") as rst:
        rst.write(heading(package, "="))
        rst.write(f".. automodule:: {package}\n\n")
        for submod in submodules:
            rst.write(heading(submod, "-"))
            rst.write(f".. automodule:: {submod}\n\n")
