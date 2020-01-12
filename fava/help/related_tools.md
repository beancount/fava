Below is a curated list of user-contributed tools for Fava & Beancount, inspired by the document [External Contributions to Beancount](http://furius.ca/beancount/doc/contrib). 

## Fava Extensions
Fava now supports [extensions]({{ url_for('help_page', page_slug='extensions') }}) including extension reports. Please submit a [pull-request](https://github.com/beancount/fava) if you have a Fava extension you'd like to appear here.

## Beancount Documentation
Documentation beyond the [original beancount user's manual](http://furius.ca/beancount/doc/index).

- [Beancount Source Code Documentation](http://aumayr.github.io/beancount-docs-static/) (Dominik Aumayr): Sphinx-generated source code documentation of the Beancount codebase. The code to produce this is [located here](https://github.com/aumayr/beancount-docs).

- [Beancount-docs to Markdown](https://github.com/xuhcc/beancount-docs) (Kirill Goncharov): Another conversion of the Google Docs using pandoc. Has less conversion artifacts.

- [SQL queries for Beancount](http://aumayr.github.io/beancount-sql-queries/) (Dominik Aumayr): Example SQL queries.

## Beancount Plugins
Beancount Plugins are usually configured in your beancount file and used for aspects of transforming, injecting, and calculating beancount data. Plugin documentation available [here](http://furius.ca/beancount/doc/scripting).

### Calculation (splitting, spreading, depreciating, recurring)

- [split_transactions](https://www.google.com/url?q=https%3A%2F%2Fgist.github.com%2Fkljohann%2Faebac3f0146680fd9aa5&sa=D&sntz=1&usg=AFQjCNGn2AkL35onTeXgOQzLzkjVpvLcpg) (Johann Klähn): Split a single transaction into many against a limbo account, as would be done for depreciation. [(discussion)](https://groups.google.com/d/msg/beancount/z9sPboW4U3c/1qIIzro4zFoJ)

- [depreciation](https://bitbucket.org/snippets/happyalu/EAMgj/beancount-automated-depreciation-plugin) (Alok Parlikar): Automatically add entries at the EOY for the depreciation of assets.

- [beancount-interpolate](https://github.com/Akuukis/beancount-interpolate) (Akuukis) : Plugins for Beancount to interpolate transactions (recur, split, depr, spread) ([PyPi](https://pypi.python.org/pypi/beancount-interpolate)).

### De-Duplication / Reimbusement

- [zerosum](https://github.com/redstreet/beancount_plugins_redstreet/tree/master/zerosum) (redstreet): [wrote a plugin](https://groups.google.com/d/msg/beancount/MU6KozsmqGQ/sehD3dqZslEJ) to match up transactions that when taken together should sum up to zero and move them to a separate account. Part of [beancount_plugins_redstreet](https://github.com/redstreet/beancount_plugins_redstreet)

### Date Manipulation

- [effective_dates](https://github.com/redstreet/beancount_plugins_redstreet/tree/master/effective_date) (redstreet): wrote a plugin to book different legs of a transaction to different dates. Part of [beancount_plugins_redstreet](https://github.com/redstreet/beancount_plugins_redstreet)

### Validation

- [file_ordering](https://github.com/zacchiro/beancount-plugins-zack) (Stefano Zacchiroli): enforces strict date ordering within individual Beancount files.

- [no\_missing\_documents](https://github.com/zacchiro/beancount-plugins-zack) (Stefano Zacchiroli): makes sure that documents referenced from Beancount exist as files on disk.

- [validate](https://github.com/zacchiro/beancount-plugins-zack) (Stefano Zacchiroli): rule-based data validation for Beancount ledgers using a simple Python-based DSL

- [cerberus_validate](https://github.com/zacchiro/beancount-plugins-zack) (Stefano Zacchiroli): rule-based data validation for Beancount ledgers using, via [Cerberus](http://docs.python-cerberus.org/en/stable/)

### Metadata

- [metadata-spray](https://github.com/seltzered/beancount-plugins-metadata-spray) (Vivek Gani): Add metadata across entries by regex expression rather than having explicit entries.

### Simplification

- [beancount-oneliner](https://github.com/Akuukis/beancount-oneliner) (Akuukis) ([PyPi](https://pypi.python.org/pypi/beancount-oneliner/1.0.0)): Plugin to write an entry in one line.

## Beancount Tools
Beancount Tools are generally either separate tools that work with beancount data, or in the case of importers or price fetchers are configured for use via your beancount's `.config` file for use with tools like `bean-extract` or `bean-price`

###Data Sourcing

####Importer Tools

- [smart_importer](https://github.com/johannesjh/smart_importer) (Johannes Harms): A smart importer for beancount and fava, with intelligent suggestions for account names.

- [beancount-import](https://github.com/jbms/beancount-import) (Jeremy Maitin-Shepard): A tool for semi-automatically importing transactions from external data sources, with support for merging and reconciling imported transactions with each other and with existing transactions in the beancount journal.  The UI is web based. ([Announcement](https://github.com/jbms/beancount-import), [link to previous version](https://groups.google.com/d/msg/beancount/YN3xL09QFsQ/qhL8U6JDCgAJ)).

####Commodity Price Sources

- [beancount-price-sources](https://github.com/hoostus/beancount-price-sources) (Justus Pendleton): A Morningstar price fetcher which aggregates multiple exchanges, including non-US ones.

- [beancount-financequote](https://github.com/andyjscott/beancount-financequote) (Andy Scott): [Finance::Quote](https://metacpan.org/release/Finance-Quote) (perl price fetching package) support for bean-price.

- [beancount-coinmarketcap](https://github.com/aamerabbas/beancount-coinmarketcap) (Aamer Abbas): Price fetcher for coinmarketcap ([see post](https://medium.com/@danielcimring/downloading-historical-data-from-coinmarketcap-41a2b0111baf)).

- [Beancount-myTools/.../iexcloud.py](https://github.com/grostim/Beancount-myTools/blob/master/price/iexcloud.py) (Timothee Gros): Price fetcher for iexcloud.

####Account Data Importers

- [yodlee importer](https://bitbucket.org/redstreet/ledgerhub/commits/5cad3e7495479b1598585a3cfcdd9a06051efcc1) (redstreet): wrote an importer for fetching data from the Yodlee account aggregator. Apparently you can get free access [as per this thread](https://groups.google.com/d/msg/beancount/nsRCbC6nP4I/Dx5NlTioDq0J).

- [plaid2text](https://github.com/madhat2r/plaid2text) (Micah Duke): An importer from [Plaid](http://www.plaid.com/) which stores the transactions to a Mongo DB and is able to render it to Beancount syntax.

- [awesome-beancount](https://github.com/wzyboy/awesome-beancount) [(Zhuoyun Wei)](https://github.com/wzyboy): A collection of importers for Chinese banks + tips and tricks.

- [beansoup](https://github.com/fxtlabs/beansoup) (Filippo Tampieri): Collection of Beancount importers and auto-completer in this project.

- [beancount-importers](https://github.com/montaropdf/beancount-importers/) (Roland Everaert): An importer to extract overtime and vacation from the SMALS timesheet format for invoicing customers.

- [beancount-dkb](https://github.com/siddhantgoel/beancount-dkb) (Siddhant Goel): importer for DKB CSV files.

- [beancount-export-patreon.js](https://gist.github.com/riking/0f0dab2b7761d2f6895c5d58c0b62a66) (Kane York): JavaScript that will export your Patreon transactions so you can see details of exactly who you've been giving money to.

- [Beancount-myTools](https://github.com/grostim/Beancount-myTools) (Timothee Gros): Personal importer tools of the author for French banks.

###Transaction Entry Tools

- [bean-add](https://github.com/simon-v/bean-add) (Simon Volpert) (CLI): A Beancount transaction entry assistant.

- [alfred-beancount](https://github.com/blaulan/alfred-beancount) (Yue Wu) (macOS/Alfred): An add-on to the "Alfred" macOS tool to quickly enter transactions in one’s Beancount file. Supports full account names and payees match.

- [Beancount Mobile](https://play.google.com/store/apps/details?id=link.beancount.mobile) (Kirill Goncharov) (Android): A mobile data entry app for Beancount. Repo:  [https://github.com/xuhcc/beancount-mobile](https://github.com/xuhcc/beancount-mobile) ([Annoucement](https://groups.google.com/d/msgid/beancount/014e0879-70e0-4cac-b884-82d8004e1b43%40googlegroups.com?utm_medium=email&utm_source=footer)).

- [costflow/syntax](https://github.com/costflow/syntax) (Leplay Li) (parsing code): A parser used for the service [costflow.io](https://www.costflow.io/) that allows users to do plain text accounting from messaging apps (Telegram, LINE, WeChat, Messenger, Whatsapp, etc.). A syntax for converting one-line message to beancount/\*ledger format.


###Tax-related Tools

- [fincen_114](https://github.com/hoostus/fincen_114) (Justus Pendleton): A FBAR / FinCEN 114 report generator.

###Portfolio Tools

- [beancount\_portfolio\_allocation](https://github.com/ghislainbourgeois/beancount_portfolio_allocation) ([Ghislain Bourgeois](https://groups.google.com/d/msgid/beancount/b36d9b67-8496-4021-98ea-0470e5f09e4b%40googlegroups.com?utm_medium=email&utm_source=footer)): A quick way to figure out the asset allocations in different portfolios.

- [portfolio-returns](https://github.com/hoostus/portfolio-returns) (Justus Pendleton): portfolio returns calculator

- [beancount\_assert\_allocation](https://github.com/redstreet/beancount_asset_allocation) (redstreet): allocation analysis tool to understand the asset allocation of a portfolio.

- [process control chart](https://github.com/hoostus/beancount-control-chart) (Justus Pendleton): Spending relative to portfolio size. [Thread.](https://groups.google.com/d/msgid/beancount/0cd47f9a-37d6-444e-8516-25e247a9e0cd%40googlegroups.com?utm_medium=email&utm_source=footer)

###Conversion Tools

####Gnucash Converters

- [gnucash-to-beancount](https://github.com/AndrewStein/gnucash-to-beancount) (Andrew Stein): A further fork from the below two, which fixes a lot of issues (see [this thread](https://groups.google.com/d/msg/beancount/MaaASKR1SSI/GX5I8lOkBgAJ)).
    - [gnucash-to-beancount](https://github.com/debanjum/gnucash-to-beancount) (Debanjum): A fork of the below.
    - [gnucash-to-beancount](https://github.com/henriquebastos/gnucash-to-beancount/) (Henrique Bastos): Original script to convert a GNUcash SQLite database into an equivalent Beancount input file.

- [pta-converters](https://gitlab.com/alensiljak/pta-converters) (Alen Šiljak) (2019): Another GnuCash to Beancount converter.

####Ynab Converters

- [beancount-ynab5](https://github.com/hoostus/beancount-ynab5) (Justus Pendleton): YNAB 5 Converter.
    - [beancount-ynab](https://github.com/hoostus/beancount-ynab) (Justus Pendleton): A converter for earlier versions of YNAB

####Ledger converters

- [ledger2beancount](https://github.com/zacchiro/ledger2beancount/) (Stefano Zacchiroli & Martin Michlmayr): A script to convert ledger files to beancount.
