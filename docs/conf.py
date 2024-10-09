from __future__ import annotations

from typing import Any

extensions = [
    "sphinx.ext.extlinks",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.intersphinx",
]
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# General information about the project.
project = "Fava"
copyright = "2016, Dominik Aumayr"  # noqa: A001
author = "Dominik Aumayr"

extlinks = {
    "bug": ("https://github.com/beancount/fava/issues/%s", "#%s"),
    "user": ("https://github.com/%s", "@%s"),
}

autodoc_default_options = {"members": True, "undoc-members": True}
typehints_use_rtype = False


def skip_namedtuples(
    _app: Any, _what: Any, _name: Any, obj: Any, _options: Any, _lines: Any
) -> bool | None:
    docstr = obj.__doc__
    if isinstance(docstr, str) and docstr.startswith("Alias for field number"):
        return True
    return None


def setup(app: Any) -> None:
    app.connect("autodoc-skip-member", skip_namedtuples)


desc = 'Web interface for <a href="http://furius.ca/beancount/">Beancount</a>'

# Set templates path to add extra links to navigation
# (in templates/sidebar/navigation.html)
templates_path = ["templates"]

# Options for HTML output
html_theme = "furo"
html_title = "Fava"
html_static_path = ["static"]
html_logo = "static/logo.png"
html_theme_options = {
    "source_repository": "https://github.com/beancount/fava/",
    "source_branch": "main",
    "source_directory": "docs/",
}
