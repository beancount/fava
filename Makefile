all: build-js

build-js: 
	cd fava/static; npm install; npm run build

clean:
	rm -r fava/static/node_modules

test:
	tox
