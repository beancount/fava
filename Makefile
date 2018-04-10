.PHONY: docs test lint binaries gh-pages bql-grammar translations-push translations-fetch before-release run-example format upload

all: fava/static/gen/app.js

fava/static/gen/app.js: fava/static/css/* fava/static/javascript/* fava/static/package.json
	rm -f fava/static/package-lock.json
	cd fava/static; npm install; npm run build

clean: mostlyclean
	rm -rf build dist
	rm -rf fava/static/gen

mostlyclean:
	rm -rf .tox
	rm -rf fava/static/node_modules
	rm -rf .*cache
	find . -type f -name '*.py[c0]' -delete
	find . -type d -name "__pycache__" -delete

lint:
	tox -e lint
	cd fava/static; npm install; npm run lint

test:
	tox

docs:
	sphinx-build -b html docs build/docs

run-example:
	BEANCOUNT_FILE= fava --debug tests/data/example.beancount

format:
	yapf -rip tests --style='{based_on_style: pep8, coalesce_brackets: True, indent_dictionary_value: True}'

bql-grammar:
	contrib/scripts.py generate_bql_grammar_json

dist: fava/static/gen/app.js fava
	rm -rf dist
	python setup.py sdist bdist_wheel

before-release: bql-grammar translations-push translations-fetch

# Before making a release, CHANGES needs to be updated and version number in
# fava/__init__.py should be set to the release version.
# A tag and GitHub release should be created too.
#
# After the release, the version number should be bumped in:
#  - fava/__init__.py (with '-dev')
#
# Also, fava.pythonanywhere.com should be updated.
upload: dist
	twine upload dist/*

# Extract translation strings and upload them to POEditor.com.
# Requires the environment variable POEDITOR_TOKEN to be set to an API token
# for POEditor.
translations-push:
	pybabel extract -F fava/translations/babel.conf -k lazy_gettext -o fava/translations/messages.pot ./fava
	contrib/scripts.py upload_translations

# Download translations from POEditor.com. (also requires POEDITOR_TOKEN)
translations-fetch:
	contrib/scripts.py download_translations

# Build and upload the website.
gh-pages:
	git checkout master
	git checkout --orphan gh-pages
	sphinx-build -b html docs _build
	ls | grep -v '_build' | xargs rm -r
	mv -f _build/* ./
	rm -r _build
	touch .nojekyll
	git add -A
	git commit -m 'Update gh-pages'
	git push --force git@github.com:beancount/fava.git gh-pages:gh-pages
	git checkout master
	git branch -D gh-pages
