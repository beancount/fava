extensions = ['sphinx.ext.extlinks']
source_suffix = '.rst'
master_doc = 'index'

# General information about the project.
project = 'fava'
copyright = '2016, Dominik Aumayr'
author = 'Dominik Aumayr'

version = __import__('fava').__version__
release = version

exclude_patterns = ['_build']
pygments_style = 'sphinx'

extlinks = {
    'bug': ('https://github.com/aumayr/fava/issues/%s', '#'),
    'user': ('https://github.com/%s', '@'),
}

# Options for HTML output
html_theme = 'alabaster'
html_static_path = ['static']
html_theme_options = {
    'logo': 'logo.png',
    'logo_name': True,
    'logo_text_align': 'center',
    'description': """Web interface for <a href=\"http://furius.ca/beancount/\"
title=\"Double-entry bookkeeping software Beancount\">Beancount</a>""",
    'github_user': 'aumayr',
    'github_repo': 'fava',
    'github_button': 'false',
    'show_powered_by': 'false',
    'extra_nav_links': {
        "fava @ Github": 'https://github.com/aumayr/fava',
        "Issue Tracker": 'https://github.com/aumayr/fava/issues',
    },
    'link': '#3572b0',
    'link_hover': '#1A2F59',
}
# html_static_path = ['_static']
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
    ]
}
htmlhelp_basename = 'favadoc'
