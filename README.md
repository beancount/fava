# beancount web

Web interface for [beancount](http://furius.ca/beancount/).

Built on [Flask](http://flask.pocoo.org/) it relies on an artificial API (`api.py`) that calls into beancount and returns Python-`dict`s for consumption by the web application. 

Many views are very buggy as this is just a quickly-hacked-together-version of what a new web interface for beancount might look like. Especially the filters (Year, Tag) are very buggy. 

This is mainly a proof-of-concept and playground for figuring out what a new web interface for beancount should look (and feel) like, and not if the (numerical) results themselves are correct or not. 

## Usage

1. Install beancount-web: `python setup.py install`.
2. Start beancount-web: `beancount-web /Volumes/Ledger/example.ledger` (substitute with the path to your own beancount-file) to run the included web server.
3. Point your browser at `http://localhost:5000` to view the web interface.

## Notable features

*(many missing here)*

### Keyboard Shortcuts

`beancount-web` comes with Gmail-style keyboard shortcuts:

<kbd>?</kbd>: Show keyboard shortcuts overview  

**Jumping to pages:**  
<kbd>g</kbd> then <kbd>i</kbd>: Go to Income Statement  
<kbd>g</kbd> then <kbd>b</kbd>: Go to Balance Sheet  
<kbd>g</kbd> then <kbd>t</kbd>: Go to Trial Balance  
<kbd>g</kbd> then <kbd>g</kbd>: Go to General Journal    
<kbd>g</kbd> then <kbd>q</kbd>: Go to Custom Query  

<kbd>g</kbd> then <kbd>h</kbd>: Go to Holdings  
<kbd>g</kbd> then <kbd>w</kbd>: Go to Net Worth  
<kbd>g</kbd> then <kbd>d</kbd>: Go to Documents  
<kbd>g</kbd> then <kbd>n</kbd>: Go to Notes  
<kbd>g</kbd> then <kbd>e</kbd>: Go to Events  
<kbd>g</kbd> then <kbd>c</kbd>: Go to Commodities  

<kbd>g</kbd> then <kbd>s</kbd>: Go to Source  
<kbd>g</kbd> then <kbd>o</kbd>: Go to Options  
<kbd>g</kbd> then <kbd>x</kbd>: Go to Statistics  
<kbd>g</kbd> then <kbd>r</kbd>: Go to Errors  

**Filtering:**  
<kbd>f</kbd> then <kbd>t</kbd>: Filter by Time      ( pull down menu)  
<kbd>f</kbd> then <kbd>g</kbd>: Filter by Tag       ( pull down menu)  
<kbd>f</kbd> then <kbd>c</kbd>: Filter by Component ( pull down menu)  
<kbd>f</kbd> then <kbd>p</kbd>: Filter by Payee     ( pull down menu)  

**Options in transaction pages:**  
<kbd>l</kbd>: show/hide legs  
<kbd>s</kbd> then <kbd>l</kbd>: show/hide legs (duplicate shortcut for consistency)  
<kbd>m</kbd>: show/hide metadata  
<kbd>s</kbd> then <kbd>m</kbd>: show/hide metadata (duplicate shortcut for consistency)  
<kbd>s</kbd> then <kbd>o</kbd>: show/hide open  
<kbd>s</kbd> then <kbd>c</kbd>: show/hide close  
<kbd>s</kbd> then <kbd>t</kbd>: show/hide transaction  
<kbd>s</kbd> then <kbd>b</kbd>: show/hide balance  
<kbd>s</kbd> then <kbd>n</kbd>: show/hide note  
<kbd>s</kbd> then <kbd>d</kbd>: show/hide document  
<kbd>s</kbd> then <kbd>p</kbd>: show/hide pad  
<kbd>s</kbd> then <kbd>P</kbd>: show/hide padding  

**Charts:**  
<kbd>Shift</kbd> + <kbd>c</kbd>: show/hide chart  
<kbd>c</kbd>: cycle through all the charts available  


---
**Caution**: This is far from finished. Consider it *alpha*-software. Contributions are very welcome :-)
