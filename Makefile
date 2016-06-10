.PHONY: docs

all: build-js

build-js:
	cd fava/static; npm install; npm run build

clean:
	rm -rf .tox
	rm -rf beancount_fava.egg-info
	rm -rf build dist
	rm -rf fava/static/node_modules

lint:
	tox -e flake8
	cd fava/static; npm install; npm run lint

test:
	tox

docs:
	sphinx-build -b html docs docs/_build

gh-pages:
	git checkout --orphan gh-pages
	sphinx-build -b html docs _build
	ls | grep -v '_build' | xargs rm -r
	mv -f _build/* ./
	rm -r _build
	touch .nojekyll
	git add -A
	git commit -m 'Update gh-pages'
	git push --force git@github.com:aumayr/fava.git gh-pages:gh-pages
	git checkout master
	git branch -D gh-pages

babel-extract:
	# Extract the translation strings from the .py- and .html-files
	pybabel extract -F fava/translations/babel.conf -k lazy_gettext -o fava/translations/messages.pot ./fava

babel-merge:
	# Merge existing .po-files with the new translation strings
	pybabel update -i fava/translations/messages.pot -d fava/translations

babel-compile:
	# Compile .po-files to binary .mo-files
	pybabel compile -d fava/translations

pyinstaller: build-js
	pyinstaller --onefile contrib/pyinstaller.spec
