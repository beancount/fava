# beancount-web: CHANGES

*Note: This file contains only user-facing changes in the 'master' branch.*

2015-12-22

  - Fixed minor styling issues

2015-12-21

  - Custom BQL queries (like with `bean-query`) can now be run in a new
    Custom Query view. The results will be displayed as a table and somewhat
    formatted, as account names will be linked to the Account view for example.

2015-12-20

  - Simple tables (Equity/Holdings, Net Worth, Events, Commodities, Options,
    Statistics, Errors) are now sortable by clicking on the column headers
    (Issue #46).

  - Added a yearly balances table to the Account-view (thanks to David 
    Stephens for the PR).

  - Limited the number of x-axis-labels for bar charts to a maximum of 25
    (Issue #45).

  - Fixed a minor bug where treemaps would show white areas (Issue #49).
  
  - Fixed daterange filtering of entries (thanks to Jakob Schnitzer for the PR)

  - Fixed values in Balance sheet to correctly calculate the closing balances
    (Issue #19)

2015-12-19

  - Added a permalink for the currently set filters, so a user can bookmark
    different filter-settings for quickly applying them (Issue #26).

(Beginning to summarize user-facing changes 2015-12-19.)
