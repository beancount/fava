There are four filters available in Fava:

- **FROM** Filter entries using a `FROM` expression as supported by the
  Beancount Query Language.
- **Time**: Filter entries by their date. You can specify dates and intervals
  like years, quarters, months, weeks, and days (for example `2015`, `2012-Q1`,
  `2010-10`, `2016-W12`, or `2015-06-12`). You can specify a range of dates like
  `2010 - 2012-10` which will display all entries between the start of 2010 and
  the end of October 2012.
  To refer to dates relative to the current day, you can use the variables
  `year`, `quarter`, `month`, `week`, and `day`. These will be substituted with
  the current date expressed in the respective format, and support addition and
  subtraction. For example you can write `year - day` for all entries in the
  current year up to today, or `year-1 - year` for all entries of the last and
  current year. To prevent subtraction, use parentheses: `(month)-10` refers to
  the 10th of this month, whereas `month-10` would be 10 months ago.
- **Tags**: Filter entries to the ones having the tags or links selected. This
  filter is inclusive, meaning that if you select multiple tags entries with any
  of those tags will be filtered. This filter also allows for negative filtering
  by prepending a `-`, e.g. `-#tag` or `-^link`, to exclude entries with the
  given tag or link.
- **Account**: Filter entries by account, matching any entry this account is
  part of. The filter can simply be an account name or a regular expression,
  e.g. `.*:Company:.*` to filter for all that contain `Company` as a component
  in the account name. If a regular expression is given, it must match the whole
  account name.
- **Payee**: Filter entries by payee. Like the account filter, this can either
  be a full payee name or a regular expression.

If you use multiple filters (like *Tags* and *Time*), the subset of entries
matching both filters will be selected.
