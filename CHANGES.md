# beancount-web: CHANGES

*Note: This file contains only user-facing changes in the 'master' branch.*

2015-12-23

  - New settings to show Journal legs by default, to show different entry types
    in a Journal by default, to hide charts by default and to show negative numbers in treemaps

  - Added new command line option "--settings" to specify a settings-file for
    beancount-web, like which entry types to display in a Journal by default.
    There is a sample file called "default-settings.conf" in the source that
    lists all possible settings.

  - Filters are now part of every URL, so every URL is a permalink to the
    view including all currently set filters (Issue #54). (Thanks to Jakob
    Schnitzer for the work on this)

2015-12-22

  - Fixed minor styling issues.

2015-12-21

  - Custom BQL queries (like with `bean-query`) can now be run in a new
    Custom Query view. The results will be displayed as a table and somewhat
    formatted, as account names will be linked to the Account view for example.

2015-12-20

  - Simple tables (Equity/Holdings, Net Worth, Events, Commodities, Options,
    Statistics, Errors) are now sortable by clicking on the column headers
    (Issue #46).

  - Added a yearly balances table to the Account-view. (Thanks to David
    Stephens for the PR)

  - Limited the number of x-axis-labels for bar charts to a maximum of 25
    (Issue #45).

  - Fixed a minor bug where treemaps would show white areas (Issue #49).

  - Fixed daterange filtering of entries. (Thanks to Jakob Schnitzer for the PR)

  - Fixed values in Balance sheet to correctly calculate the closing balances
    (Issue #19).

2015-12-19

  - Added a permalink for the currently set filters, so a user can bookmark
    different filter-settings for quickly applying them (Issue #26).

(Beginning to summarize user-facing changes 2015-12-19.)
