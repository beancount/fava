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

extlinks = {
    'bug': ('https://github.com/aumayr/fava/issues/%s', '#'),
    'user': ('https://github.com/%s', ''),
}

# Options for HTML output
html_theme = 'alabaster'
html_theme_options = {
    'github_user': 'aumayr',
    'github_repo': 'fava',
    'github_button': 'false',
    'show_powered_by': 'false',
    'extra_nav_links': {
        "fava @ Github": 'https://github.com/aumayr/fava',
        "Issue Tracker": 'https://github.com/aumayr/fava/issues',
    },
}
html_static_path = ['_static']
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
    ]
}
htmlhelp_basename = 'favadoc'
