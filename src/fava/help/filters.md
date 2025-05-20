# Filters

With the text inputs at the top right of the page, you can filter the entries
that are displayed in Fava's reports. If you use multiple filters, the entries
matching all of them will be selected.

## Time

Filter entries by their date. You can specify dates and intervals like years,
quarters, months, weeks, and days (for example `2015`, `2012-Q1`, `2010-10`,
`2016-W12`, or `2015-06-12`). You can specify a range of dates like
`2010 - 2012-10` which will display all entries between the start of 2010 and
the end of October 2012.

To refer to dates relative to the current day, you can use the variables `year`,
`quarter`, `month`, `week`, and `day`. These will be substituted with the
current date expressed in the respective format, and support addition and
subtraction. For example you can write `year - day` for all entries in the
current year up to today, or `year-1 - year` for all entries of the last and
current year. To prevent subtraction, use parentheses: `(month)-10` refers to
the 10th of this month, whereas `month-10` would be 10 months ago.

### Summarisation of previous balances and conversions

When setting a time filter, Fava does not just filter to the transactions in the
interval but also summarises transactions in the following ways (using
Beancount's "clamp" summarisation):

- All balances for the Income and Expenses accounts previous to the filtered
  period are transferred to the `account_previous_earnings` ("retained
  earnings") account and all of the other transactions before begin date are
  summarised against the `account_previous_balances` account (usually "opening
  balances"). So the Income and Expenses start with a balance of zero whereas
  Assets and Liabilities accounts start with their accumulated balance.
- All the entries after the end date are removed.
- A conversion entry is added to the `account_current_conversions` account for
  the changes occurring within the filtered period.

### ISO 8601 Week dates

The week-based calendar follows
[ISO 8601 week-numbering system](https://en.wikipedia.org/wiki/ISO_week_date)
with each week starting on Mondays and the first week of the ISO week-based year
being the first week that has the majority of its days in January. Equivalently,
it is also the week to containing January 4th.

Some examples where the ISO week-based calendar differs from the Gregorian
calendar:

- Week 1 of 2025 starts on Monday 30 December 2024 and ends on Sunday 5 January
  2025\. As a result, 30 December 2024 belongs to the year 2025 of the ISO
  week-based calendar, despite being in the year 2024 of the Gregorian calendar.
- Week 53 of 2020 ends on Sunday 3 January 2021. As a result, 3 January 2021
  belongs to the year 2020 of the ISO week-based calendar, despite being in the
  year 2021 of the Gregorian calendar.

Most years of ISO week-based calendars have 52 weeks, but as there are slightly
more than 52 weeks in a year, some years contain a 53rd week.

## Account

Filter entries by account, matching any entry this account is part of. The
filter can be an account name, either the full account name or a component of
the account name, or a regular expression matching the account name, e.g.
`.*Company.*` to filter for all that contain `Company`.

## Filter by tag, link, payee and other metadata

This final filter allows you to filter entries by various attributes.

- Filter by `#tag` or `^link`.
- Filter by amount, such as `= 100.20` or `>= 100` (comparing the absolute of
  the units).
- Filter by any entry attribute, such as payee `payee:"restaurant"` or narration
  `narration:'Dinner with Joe'`. The argument is a regular expression which
  needs to be quoted (with `'` or `"`) if it contains spaces or special
  characters. If the argument is not a valid regular expression, Fava will look
  for an exact match instead.
- Search in payee and narration if no specific entry attribute is given, e.g.
  `"Cash withdrawal"`. For Note directives, the comment will be searched.
- Filter for entries having certain metadata values: `document:"\.pdf$"`. Note
  that if the entry has an attribute of the same name as the metadata key, the
  filter will apply to the entry attribute, not the metadata value.
- Exclude entries that match a filter by prepending a `-` to it, e.g. `-#tag` or
  `-(^link #tag)`.
- To match entries by posting attributes, you can use `any()` and `all()`, e.g.,
  `any(id:'12', account:"Cash$")` for all entries that have at least one posting
  with metadata `id: 12` or account ending in `Cash`, or
  `all(-account:"^Expenses:Food")` to exclude all transactions having a posting
  to the Expenses:Food account. To match by amount, you can use comparison
  operators, e.g. `any(units > 80)` to filter for all entries where one posting
  has a units with an absolute amount greater than 80.

These filters can be combined by separating them by spaces to match all entries
satisfying all given filters or by commas to match all entries satisfying at
least one of the given filters. In other words, a space acts like an "and" and a
comma like an "or". As usual, the logical "and" has a higher grouping power than
"or" and you can use parentheses to group filters.

When given regular expressions, Fava checks for a match anywhere in the
corresponding attribute. Matching is always case-insensitive. To find out more
about the specific syntax Fava uses, refer to
[Python's Regular Expression Syntax](https://docs.python.org/3/library/re.html?highlight=match#regular-expression-syntax).
