# Steps to create a release

1. Compare changes to last release, e.g.
   https://github.com/beancount/fava/compare/v1.1...master
1. Update `CHANGES`.
1. Update `AUTHORS`.
1. Ensure tests pass.
1. Update version number in `fava/__init__.py`
1. Compile SCSS + JS with `make`
1. Upload to PyPI with `python setup.py sdist bdist_wheel upload`
1. Make a Github release
1. Update to newest version on http://fava.pythonanywhere.com
