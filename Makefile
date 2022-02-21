FRONTEND_SOURCES := $(shell find frontend/src frontend/css -type f)
TRANSLATION_SOURCES := $(wildcard src/fava/translations/*/LC_MESSAGES/messages.po)
TRANSLATION_TARGETS := $(TRANSLATION_SOURCES:messages.po=messages.mo)

.PHONY: all
all: src/fava/static/app.js $(TRANSLATION_TARGETS)

src/fava/static/app.js: $(FRONTEND_SOURCES) frontend/build.ts frontend/node_modules
	rm -f src/fava/static/*
	git checkout -- src/fava/static
	cd frontend; npm run build

frontend/node_modules: frontend/package-lock.json
	cd frontend; npm install --no-progress
	touch -m frontend/node_modules

$(TRANSLATION_TARGETS): $(TRANSLATION_SOURCES)
	pybabel compile -d src/fava/translations

.PHONY: clean
clean: mostlyclean
	find src/fava/static ! -name 'favicon.ico' -type f -exec rm -f {} +

.PHONY: mostlyclean
mostlyclean:
	rm -rf .*cache
	rm -rf .eggs
	rm -rf .tox
	rm -rf build
	rm -rf dist
	rm -rf frontend/node_modules
	find . -type f -name '*.py[c0]' -delete
	find . -type d -name "__pycache__" -delete
	find src/fava/translations -name '*.mo' -delete

.PHONY: lint
lint: frontend/node_modules
	pre-commit run -a
	cd frontend; npx tsc
	cd frontend; npx svelte-check
	tox -e lint

.PHONY: test
test:
	cd frontend; npm run build
	cd frontend; npm run test
	tox -e py

.PHONY: update-snapshots
update-snapshots:
	find . -name "__snapshots__" -type d -prune -exec rm -r "{}" +
	-SNAPSHOT_UPDATE=1 tox -e py
	tox -e py

.PHONY: update-deps
update-deps:
	-cd frontend; npm outdated
	cd frontend; npm update
	cd frontend; npm run sync-pre-commit
	touch -m frontend/node_modules

.PHONY: update-precommit
update-precommit:
	pre-commit autoupdate

.PHONY: docs
docs:
	tox -e docs

.PHONY: run-example
run-example:
	@xdg-open http://localhost:3333
	BEANCOUNT_FILE= fava -p 3333 --debug tests/data/*.beancount

.PHONY: bql-grammar
bql-grammar:
	contrib/scripts.py generate-bql-grammar-json

dist: src/fava/static/app.js src/fava setup.cfg pyproject.toml MANIFEST.in
	rm -rf build dist
	tox -e build-dist

.PHONY: before-release
before-release: bql-grammar translations-push translations-fetch

# Before making a release, CHANGES needs to be updated and
# a tag should be created too.
#
# Also, fava.pythonanywhere.com should be updated.
.PHONY: upload
upload: dist
	twine upload dist/*

# Extract translation strings.
.PHONY: translations-extract
translations-extract:
	pybabel extract -F src/fava/translations/babel.conf -o src/fava/translations/messages.pot .

# Extract translation strings and upload them to POEditor.com.
# Requires the environment variable POEDITOR_TOKEN to be set to an API token
# for POEditor.
.PHONY: translations-push
translations-push: translations-extract
	contrib/scripts.py upload-translations

# Download translations from POEditor.com. (also requires POEDITOR_TOKEN)
.PHONY: translations-fetch
translations-fetch:
	contrib/scripts.py download-translations

# Build and upload the website.
.PHONY: gh-pages
gh-pages:
	git checkout main
	git checkout --orphan gh-pages
	tox -e docs
	ls | grep -v 'build' | xargs rm -r
	mv -f build/docs/* ./
	rm -r build .builds .github
	touch .nojekyll
	git add -A
	git commit -m 'Update gh-pages' --no-verify
	git push --force git@github.com:beancount/fava.git gh-pages:gh-pages
	git checkout main
	git branch -D gh-pages

# Create a binary using pyinstaller
dist/fava: src/fava/static/app.js
	tox -e pyinstaller
