.PHONY: node_modules

all: node_modules bin/fava

node_modules:
	npm update

bin/fava:
	make -C ..
	make -C .. pyinstaller
	mkdir -p bin
	cp ../dist/fava bin/fava

clean:
	rm -rf bin dist
	rm -rf node_modules

lint: node_modules
	`npm bin`/eslint src/main.js

dist: node_modules bin/fava
	`npm bin`/build

# Requires imagemagick's convert
icons: build/icon.icns build/icon.ico

build/icon.ico: icon.svg
	convert -background none -define icon:auto-resize=256,128,48,32,16 icon.svg build/icon.ico

build/icon.icns: icon.svg
	mkdir -p build/Fava.iconset
	convert -background none -resize 16x16 icon.svg build/Fava.iconset/icon_16x16.png
	convert -background none -resize 32x32 icon.svg build/Fava.iconset/icon_32x32.png
	cp build/Fava.iconset/icon_32x32.png build/Fava.iconset/icon_16x16@2x.png
	convert -background none -resize 64x64 icon.svg build/Fava.iconset/icon_32x32@2x.png
	convert -background none -resize 128x128 icon.svg build/Fava.iconset/icon_128x128.png
	convert -background none -resize 256x256 icon.svg build/Fava.iconset/icon_256x256.png
	cp build/Fava.iconset/icon_256x256.png build/Fava.iconset/icon_128x128@2x.png
	convert -background none -resize 512x512 icon.svg build/Fava.iconset/icon_512x512.png
	cp build/Fava.iconset/icon_512x512.png build/Fava.iconset/icon_256x256@2x.png
	convert -background none -density 1024 -resize 1024x1024 icon.svg build/Fava.iconset/icon_512x512@2x.png
	iconutil --convert icns --output build/icon.icns build/Fava.iconset
	rm -r build/Fava.iconset
