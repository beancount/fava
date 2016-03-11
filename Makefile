.PHONY: docs

all: build-js

build-js: 
	cd fava/static; npm install; npm run build

clean:
	rm -r fava/static/node_modules

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
