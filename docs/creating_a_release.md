# Steps to create a release

1. Compare changes to last release, eg.
   https://github.com/aumayr/fava/compare/v0.2.2...master
2. Create release notes in `RELEASENOTES.md`
3. Update `CHANGES.md`
4. Update `README.rst` (search and replace old version number)
5. Update `AUTHORS.md`
6. Search for old version number and replace with new one where appropriate
7. Update version number in `fava/__init__.py`
8. Compile SCSS + JS with `make build-js`
9. Run `make test` to ensure tests pass
10. Commit changes
11. Upload to PyPI with `python setup.py sdist bdist_wheel upload`
12. Make a Github release
13. Update to newest version on http://fava.pythonanywhere.com
