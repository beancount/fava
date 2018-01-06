With the text inputs at the top right of the page, you can filter the entries
that are displayed in Fava's reports.  If you use multiple filters, the subset
of entries matching all active filters will be selected.

### Time

Filter entries by their date. You can specify dates and intervals like years,
quarters, months, weeks, and days (for example `2015`, `2012-Q1`, `2010-10`,
`2016-W12`, or `2015-06-12`). You can specify a range of dates like
`2010 - 2012-10` which will display all entries between the start of 2010 and
the end of October 2012.  To refer to dates relative to the current day, you
can use the variables `year`, `quarter`, `month`, `week`, and `day`. These will
be substituted with the current date expressed in the respective format, and
support addition and subtraction. For example you can write `year - day` for
all entries in the current year up to today, or `year-1 - year` for all entries
of the last and current year. To prevent subtraction, use parentheses:
`(month)-10` refers to the 10th of this month, whereas `month-10` would be 10
months ago.

### Account

Filter entries by account, matching any entry this account is part of. The
filter can be an account name, either the full account name or a component of
the account name, or a regular expression matching the account name, e.g.
`.*Company.*` to filter for all that contain `Company`.

### Filter by tag, link, payee and other metadata

This final filter allows you to filter entries by various attributes.

- Filter by `#tag` or `^link`.
- Filter by payee `payee:".*restaurant.*"`, or narration `narration:'Dinner with Joe'`,
  or any other entry attribute. The argument needs to be quoted (with `'` or
  `"`) if it contains spaces and can either be simply a string or a regular
  expression that matches the attribute.
- Filter entries using a `FROM` expression as supported by the
  Beancount Query Language: `from:'year = 2012'`.
- Filter for entries having certain metadata values: `statement:".*pdf"`.
- Exclude entries that match a filter by prepending a `-` to it, e.g. `-#tag`
  or `-(^link #tag)`.

These filters can be combined by separating them by spaces to match all entries
satisfying all given filters or by commas to match all entries satisfying at
least one of the given filters. In other words, a space acts like an "and" and
a comma like an "or". As usual, the logical "and" has a higher grouping power
than "or" and you can use parentheses to group filters.
