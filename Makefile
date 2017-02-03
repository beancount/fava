.PHONY: docs test lint binaries gh-pages

all: fava/static/gen/app.js

fava/static/gen/app.js: fava/static/sass/* fava/static/javascript/*
	cd fava/static; npm update; npm run build

clean: mostlyclean
	rm -rf build dist
	rm -rf fava/static/gen

mostlyclean:
	rm -rf .tox
	rm -rf fava/static/node_modules
	find . -type f -name '*.py[c0]' -delete
	find . -type d -name "__pycache__" -delete

lint:
	tox -e lint
	cd fava/static; npm update; npm run lint

test:
	tox

docs:
	sphinx-build -b html docs docs/_build

# This requires Vagrant (with vagrant-scp plugin) and Virtualbox (with
# Extension Pack) to be installed. This might take quite some time -
# especially on the first run, when the VM images have to be downloaded.
binaries: dist/fava-linux-x64 dist/fava-macos-x64
dist/fava-linux-x64: fava fava/static/gen/app.js
	vagrant up centos
	vagrant scp centos:/vagrant/fava/dist/fava dist/fava-linux-x64
	vagrant halt centos
dist/fava-macos-x64: fava fava/static/gen/app.js
	vagrant up darwin
	vagrant scp darwin:/vagrant/fava/dist/fava dist/fava-macos-x64
	vagrant halt darwin

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

# Extract the translation strings from the .py- and .html-files
babel-extract:
	pybabel extract -F fava/translations/babel.conf -k lazy_gettext -o fava/translations/messages.pot ./fava

# Merge existing .po-files with the new translation strings
babel-merge:
	pybabel update -i fava/translations/messages.pot -d fava/translations

# Compile .po-files to binary .mo-files
babel-compile:
	pybabel compile -d fava/translations

pyinstaller:
	pyinstaller --clean --onefile contrib/pyinstaller.spec
