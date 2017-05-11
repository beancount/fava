.PHONY: docs test lint binaries gh-pages

all: fava/static/gen/app.js

fava/static/gen/app.js: fava/static/css/* fava/static/javascript/*
	cd fava/static; npm update; npm run build

clean: mostlyclean
	rm -rf build dist
	rm -rf fava/static/gen
	make -C gui clean

mostlyclean:
	rm -rf .tox
	rm -rf fava/static/node_modules
	find . -type f -name '*.py[c0]' -delete
	find . -type d -name "__pycache__" -delete

lint:
	tox -e lint
	cd fava/static; npm update; npm run lint
	make -C gui lint

test:
	tox

docs:
	sphinx-build -b html docs build/docs

# Extract the translation strings from the .py- and .html-files
babel-extract:
	pybabel extract -F fava/translations/babel.conf -k lazy_gettext -o fava/translations/messages.pot ./fava

# Merge existing .po-files with the new translation strings
babel-merge:
	pybabel update -i fava/translations/messages.pot -d fava/translations

# Compile .po-files to binary .mo-files
babel-compile:
	pybabel compile -d fava/translations

pyinstaller: dist/fava fava/static/gen/app.js
dist/fava: fava
	pyinstaller --clean --onefile contrib/pyinstaller.spec

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
