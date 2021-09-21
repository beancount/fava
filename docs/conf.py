# pylint: disable=invalid-name,missing-docstring,redefined-builtin

extensions = [
    "sphinx.ext.extlinks",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
]
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# General information about the project.
project = "Fava"
copyright = "2016, Dominik Aumayr"
author = "Dominik Aumayr"

extlinks = {
    "bug": ("https://github.com/beancount/fava/issues/%s", "#"),
    "user": ("https://github.com/%s", "@"),
}

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
}


def skip_namedtuples(_app, _what, _name, obj, _options, _lines):
    docstr = obj.__doc__
    if isinstance(docstr, str) and docstr.startswith("Alias for field number"):
        return True
    return None


def setup(app):
    app.connect("autodoc-skip-member", skip_namedtuples)


desc = 'Web interface for <a href="http://furius.ca/beancount/">Beancount</a>'
# Options for HTML output
html_theme = "alabaster"
html_static_path = ["static"]
html_theme_options = {
    "logo": "logo.png",
    "logo_name": True,
    "logo_text_align": "center",
    "description": desc,
    "github_user": "beancount",
    "github_repo": "fava",
    "github_button": "false",
    "show_powered_by": "false",
    "extra_nav_links": {
        "fava @ GitHub": "https://github.com/beancount/fava",
        "Chat": "https://gitter.im/beancount/fava",
        "Issue Tracker": "https://github.com/beancount/fava/issues",
    },
    "link": "#3572b0",
    "link_hover": "#1A2F59",
}
# html_static_path = ['_static']
html_sidebars = {"**": ["about.html", "navigation.html"]}
htmlhelp_basename = "favadoc"
