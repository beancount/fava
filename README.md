# beancount web

Web interface for [beancount](http://furius.ca/beancount/).

Built on [Flask](http://flask.pocoo.org/) it relies on an artificial API (`api.py`) that calls into beancount and returns Python-`dict`s for consumption by the web application. 

Many views are very buggy as this is just a quickly-hacked-together-version of what a new web interface for beancount might look like. Especially the filters (Year, Tag) are very buggy. 

This is mainly a proof-of-concept and playground for figuring out what a new web interface for beancount should look (and feel) like, and not if the (numerical) results themselves are correct or not. 

## Usage

A `bin`-file for running it directly off a command line prompt is still missing. Therefore you have to run it off a Python prompt.

1. Open a `python`-prompt (Python 3 required)
2. `from beancount_web import application` to import the web application
3. `application.run('/Volumes/Ledger/example.ledger')` (substitute with the path to your own beancount-file) to run the included web server.
4. Point your browser at `http://localhost:5000` to view the web interface. 

--- 
**Caution**: This is far from finished. Consider it *alpha*-software. Contributions are very welcome :-)
