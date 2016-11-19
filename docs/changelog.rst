Changelog
=========

v1.1 (November 19th, 2016)
--------------------------

You can now upload documents by dropping them onto transactions, which will
also add the file path as `statement` metadata to the transaction. Fava also
ships with a plugin to link these transactions with the generated documents.
See the help pages for details.

This is the first release for which we provide compiled binaries (for macOS and
Linux). These do not have any dependencies and can simply be executed from the
terminal.

Other changes:

- The bar charts on account pages now also show budgets.
- The Journal can now be sorted by date, flag and narration.
- Fava now has a Russian translation, thanks to :user:`fokusov`.
- As always, several bugs have been fixed.

Thanks to :user:`adamgibbins` and :user:`xentac` for their contributions.

v1.0 (October 19th, 2016)
-------------------------

This is a major new release that includes too many improvements and changes to
list. Some highlights:

- The layout has been tweaked and we use some nicer fonts.
- Fava looks and works much better on smaller screens.
- Fava loads most pages asynchronously, so navigating Fava is much faster and
  responsive.

Fava's configuration is not read from a configuration file anymore but can
rather be specified using custom entries in the Beancount file. Some options
have also been removed or renamed, so check Fava's help page on the available
options when upgrading from v0.3.0.

There have been many changes under the hood to improve Fava's codebase and a
lot of bugs have been squashed.

Thanks to :user:`adamgibbins`, :user:`davidastephens`, :user:`xentac`, and
:user:`yegle` for their contributions.

v0.3.0 (May 24th, 2016)
-----------------------

Additions

- Support for switching between multiple beancount files. :bug:`213`
- New sunburst charts. :bug:`198`
- Add "Clear filter" button when filters are active. :bug:`290`
- Simple budgeting functionality in the Account view. See help pages on how to
  use budgets. :bug:`294`
- German translation. :bug:`284`
- The Beancount is now being reloaded when it is saved in the Source Editor.
- New Journal filter controls. Thanks to :user:`yagebu`.
- Tree-tables are now displayed in a hierachical way. Thanks to :user:`yagebu`.

Changes

- All charts are now rendered with d3.js. Thanks to :user:`yagebu`.
- The title of a page is now shown in the header to save screen space.
- Changed shortcut for Journal from ``g g`` to ``g j`` as the Journal was
  renamed from "General Journal" to "Journal".

New configuration options

- ``language``: The language to use. Valid languages are ``"en"`` and
  ``"de"`` (default: ``"en"``). :bug:`284`
- ``treemaps-show-negative-numbers`` was removed.

Fixes

- Commodity prices are now filtered when a Time filter is enabled. :bug:`273`
- Some improvements to the help pages.
- Many small bug fixes. Thanks to :user:`yagebu`.

v0.2.6 (March 20th, 2016)
-------------------------

Additions

- There are now more interval options available for charts and the account
  balances report. The interval can be selected from a dropdown next to the
  charts. :bug:`175`
- Show metadata for postings in the Journal. Thanks to :user:`corani`.
  :bug:`185`
- The editor now supports org-mode style folding. Thanks to :user:`corani`.
  :bug:`209`
- Show colored dots for all the postings of a transaction in the Journal
  report. This way flagged postings can be quickly spotted. :bug:`195`
- Add keyboard shortcuts for save to source editor. :bug:`199`

Changes

- Use beancount's DisplayContext to determine the correct precision at which to
  render numbers. :bug:`188`
- Improve the way that query results are serialized to XLS etc. Thanks to
  :user:`corani`. :bug:`168`
- Show inverse rates for pairs of operating currencies on the commodities
  report. :bug:`139`
- Use Click for the CLI and check if beancount file exists on startup.
  :bug:`216`
- Hide closed accounts in tree tables. Also see new configuration option below.

New configuration options

- ``editor-strip-trailing-whitespace`` to enable trimming of trailing
  whitespace in the Source editor (default: "false").  Thanks to
  :user:`corani`. :bug:`163`
- ``show-closed-accounts`` to show closed accounts in tree tables, for example
  on the balance sheet (default: "false"). :bug:`91`
- ``show-accounts-with-zero-balance`` to show accounts with a balance of zero
  in tree tables (default: "true"). :bug:`91`
- ``show-accounts-with-zero-transactions`` to show accounts with no
  transactions in tree tables (default: "true"). :bug:`91`

Fixes

- Fixed a bug where the months would be off by one for the interval reports.
  :bug:`182`
- Fix the net worth report for more than one currency. :bug:`207`
- Some improvements to the help pages.
- Many small bug fixes.

v0.2.5 (February 28th, 2016)
----------------------------

Bump release to remove unused draft code.

v0.2.4 (February 28th, 2016)
----------------------------

Additions

- Added missing Holdings views compared to ``bean-web``. Thanks to
  :user:`yagebu`. :bug:`140`
- Custom queries are now shown in sidebar. Thanks to :user:`corani`. :bug:`135`
- The user settings file is now editable in the Source editor. :bug:`136`
- Added second theme. Thanks to Rubén Gómez for the stylesheet. :bug:`59`
- Added Help pages.
- Query results can now be downloaded as CSV, XLS, XLSX and ODS. :bug:`143`
- Documents can now be uploaded by dragging and dropping files over an Account
  name on the Account page and all tree-tables. :bug:`157`
- Journal can now be filtered by transaction type. Thanks to :user:`yagebu`.

Changes

- The uptodate-indicator is now shown everywhere by default, but only enabled
  for accounts that have the metadata ``fava-uptodate-indication: "True"`` set
  on their ``open``-directives. :bug:`35`
- Speedier Journal rendering. Thanks to :user:`yagebu`. :bug:`164`
- Only basenames will be shown for documents in the Journal. Thanks to
  :user:`corani`.
- Slightly reordered the sidebar menu.
- Minor UI tweaks.

New configuration options

- ``sidebar-show-queries``: The maximum number of custom queries to show in the
  sidebar (default: 5).
- ``theme``: The theme to use. Valid themes are ``"default"`` and
  ``"alternative"`` (default: ``"default"``).
- ``editor-print-margin-column``: Set the column for the print margin in the
  Source editor (default: 60). :bug:`161`
- ``uptodate-indicator-show-everywhere`` (default: "true"). See Changes above.

Removed configuration options

- ``uptodate-indicator-exclude-accounts``, see Changes above.

Fixes

- Fixed Net worth calculation. Thanks to :user:`yagebu`.
- Many small bug fixes.

v0.2.3 (February 15th, 2016)
----------------------------

Bumped version to communicate that installing via ``pip install`` now works,
all requirements included.  Thanks to :user:`blais` and :user:`yagebu`.


Earlier Versions
----------------

It was not possible to install any of the earlier versions only using `pip`,
but if you used a source install prior to this point, here are the user-facing
changes going back to December 19th, 2015. The first commit in the git
repository was on December 4th, 2015.

v0.2.2 (February 14th, 2016)

- Fixed `setup.py` to include missing dependencies and exclude unused static
  assets.

v0.2.1 (February 13th, 2016)

- Bumped version due to changes in how JavaScript and CSS are handled
  internally. Thanks to :user:`yagebu`. :bug:`125`

v0.2.0 (February 11th, 2016 - first release of `fava`)

- Renamed the project from "beancount-web" to "fava". :bug:`85`
- Moved ``beancount-urlscheme``-command to it's own `project
  <http://github.com/aumayr/beancount_urlscheme>`__.
- 2016-01-30 - Include today in the ``Year to Date`` filter. Thanks to
  :user:`corani`.
- 2016-01-30 - Legs now collapse correctly in the Journal view. Thanks to
  :user:`corani`.
- 2016-01-20 - New favicon. :bug:`90`
- 2016-01-18 - Display QUERY directives in a dropdown in the Custom Query view.
  Thanks to :user:`corani` and :user:`yagebu` for help. :bug:`96`
- 2016-01-14 - Prevent metadata keys from linewrapping
- 2016-01-11 - Hide filters on pages where they are not used.  Thanks to
  :user:`corani`. :bug:`97`
- 2016-01-09 - Added Windows/Cygwin-support to ``beancount-urlscheme``.  Thanks
  to :user:`redstreet`.:bug:`92`
- 2016-01-07 - Added setting ``collapse-accounts`` to specify a list of
  accounts to collapse in the account hierachy. :bug:`91`
- 2016-01-07 - Added a ``beancount-urlscheme``-command to register the
  ``beancount://``-URL -scheme on a Mac (other platforms still missing, but in
  development). There is a new setting called ``use-external-editor`` that
  will, if set to ``True``, render all links to the Source Editor als
  ``beancount://``-URLs to open the files directly in the editor specified by
  the ``external-editor-cmd``-setting (The URL-scheme has to be registerd with
  ``beancount-urlscheme`` first). This also renders the Source Editor view as
  readonly. :bug:`92`
- 2015-12-28 - Added new setting (and feature) called ``editor-insert-marker``.
  If present, the Source editor will jump to the specified marker in the file
  and will insert two newlines above it and set the cursor there. :bug:`76`
- 2015-12-28 - Bar chart bars are now clickable and will set the time filter to
  the year and month the bar is representing.
- 2015-12-28 - Line charts are now zoomable by drawing a rectangle with the
  mouse on the chart, which will then zoom to the specified area.
- 2015-12-28 - Added keyboard shortcuts for jumping to menu items, open and
  focus filters, Journal entry types and more. Press ? to display an overview
  of all keyboard shortcuts. Thanks to :user:`redstreet` for the suggestions.
  :bug:`65`
- 2015-12-27 - Source editor now supports auto-completion of accounts,
  commodities, directives and tags.
- 2015-12-25 - Entries can now be filtered for "No payee" Thanks to
  :user:`yagebu`. :bug:`42`
- 2015-12-24 - Metadata is now displayed for Journal entries. For transactions,
  if there is a metadata-entry called "statement" and it's value is a path to a
  file (relative to the beancount-file or absolute), this file will be liked.
- 2015-12-23 - Up-to-date indicator will be shown for Assets and Liabilities
  accounts in the Statistics view that indicates (there are various settings to
  change the behaviour of these indicators::

       green:  The latest posting is a balance check that passed.
       red:    The latest posting is a balance check that failed.
       yellow: The latest posting is not a balance check.
       gray:   The account hasn't been updated in a while.

- 2015-12-23 - New settings to show Journal legs by default, to show different
  entry types in a Journal by default, to hide charts by default and to show
  negative numbers in treemaps
- 2015-12-23 - Added new command line option "--settings" to specify a
  settings-file for beancount-web, like which entry types to display in a
  Journal by default. There is a sample file called "default-settings.conf" in
  the source that lists all possible settings.
- 2015-12-23 - Filters are now part of every URL, so every URL is a permalink
  to the view including all currently set filters. Thanks to :user:`yagebu`.
  :bug:`54`
- 2015-12-21 - BQL queries (like with ``bean-query``) can now be run in a new
  Query view.  The results will be displayed as a table and somewhat formatted,
  as account names will be linked to the Account view for example.
- 2015-12-20 - Simple tables are now sortable by clicking on the column
  headers.  :bug:`46`
- 2015-12-20 - Added a yearly balances table to the Account-view. Thanks to
  :user:`davidastephens`.
- 2015-12-20 - Show at most 25 x-axis-labels for bar charts. :bug:`45`
- 2015-12-20 - Fixed a minor bug where treemaps would show white areas.
  :bug:`49`
- 2015-12-20 - Fixed daterange filtering of entries. Thanks to :user:`yagebu`.
- 2015-12-20 - Fixed values in Balance sheet to correctly calculate the closing
  balances. :bug:`19`
