---
title: Fava's features
---

# Fava's features

This is an overview that might help you use some of the more advanced features
that fava offers.

## Keyboard Shortcuts

`fava` comes with Gmail-style keyboard shortcuts: Press <kbd>?</kbd> on any page
to show an overview of the keyboard shortcuts described below.

## Filters

There are four filters available in `fava`:

- **Time**: Filter entries by their date. This filter does some free-text
  recognition, which means you can enter terms like `This Month`, `2015-03`,
  `March 2015`, `Mar 2015`, `Last Year`, `Aug Last Year`, `2010-10 - 2014` or
  `Year to Date`
- **Tags**: Filter entries to the ones having the tags selected. This filter is
  inclusive, meaning that if you select multiple tags entries with any of those
  tags will be filtered.
- **Account**: Filter entries by account, matching any entry where this account
  is part of.
- **Payee**: Filter entries by payee. This filter is, like the *Tags*-filter,
  inclusive.

If you select multiple filters (like *Tags* and *Time*), the subset of entries
matching both filters will be selected.

## Up-to-date indicators

fava offers colored indicators that can help you keep your accounts up-to-date.
They are shown everywhere by default, but only enabled for accounts that have
the metadata `fava-uptodate-indication: "True"` set on their Open directive.
The colours have the following meaning.

- green: The last entry for this account is a balance check that passed.
- red: The last entry is a balance check that failed.
- yellow: The last entry is not a balance check.
- gray: The account has not been updated in a while, as set by the
  `uptodate-indicator-grey-lookback-days` configuration variable.
