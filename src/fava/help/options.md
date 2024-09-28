# Options

To customize some of Fava's behaviour, you can add custom entries like the
following to your Beancount file.

<pre><textarea is="beancount-textarea">
2016-06-14 custom "fava-option" "default-file"
2016-04-14 custom "fava-option" "auto-reload" "true"
2016-04-14 custom "fava-option" "currency-column" "100"</textarea></pre>

Below is a list of all possible options for Fava.

---

## `language`

Default: Not set

If this setting is not specified, Fava will try to guess the language from your
browser settings. Fava currently ships translations into the following
languages:

- Bulgarian (`bg`)
- Catalan (`ca`)
- Chinese (`zh_CN` and `zh_TW`)
- Dutch (`nl`)
- English (`en`)
- French (`fr`)
- German (`de`)
- Persian (`fa`)
- Portuguese (`pt` and `pt_BR`)
- Russian (`ru`)
- Slovak (`sk`)
- Spanish (`es`)
- Swedish (`sv`)
- Ukrainian (`uk`)

---

## `locale`

Default: Not set or `en` if the Beancount `render_commas` option is set.

This sets the locale that is used to render out numbers. For example, with the
locale `en_IN` the number `1111111.33` will be rendered `11,11,111.33`,
`1,111,111.33` with locale `en`, or `1.111.111,33` with locale `de`.

---

## `default-file`

Use this option to specify a default file for the editor to open. This option
may optionally take a value of a filename to be the default. If you don't
provide a filename, the file this custom option is in is used.

---

## `default-page`

Default: `income_statement/`

Use this option to specify the page to be redirected to when visiting Fava. If
this option is not specified, you are taken to the income statement. You may
also use this option to set filters. For example, a `default-page` of
`balance_sheet/?time=year-2+-+year` would result in you being redirected to a
balance sheet reporting the current year and the two previous years.

Note that the supplied path is relative. It is probably easiest to navigate to
the URL in your browser and copy the portion of the URL after the 'title' of
your beancount file into this option.

---

## `fiscal-year-end`

Default: `12-31`

The last day of the fiscal (financial or tax) period for accounting purposes in
`%m-%d` format. Allows for the use of `FY2018`, `FY2018-Q3`, `fiscal_year` and
`fiscal_quarter` in the time filter, and `FY2018` as the start date, end date,
or both dates in a date range in the time filter. Month can be a value larger
than `12` to have `FY2018` end in 2019 for example.

Examples are:

- `04-05` - UK
- `06-30` - Australia / NZ
- `09-30` - US federal government
- `15-31` - Japan

See [Fiscal Year on WikiPedia](https://en.wikipedia.org/wiki/Fiscal_year) for
more examples.

---

## `indent`

Default: 2.

The number spaces for indentation.

---

## `insert-entry`

Default: Not set.

This option can be used to specify where entries are inserted. The argument to
this option should be a regular expression matching account names. This option
can be given multiple times. When adding an entry, the account of the entry (for
a transaction, the account of the last posting is used) is matched against all
`insert-entry` options and the entry will be inserted before the datewise latest
of the matching options before the entry date. If the entry is a Transaction and
no `insert-entry` option matches the account of the last posting the account of
the second to last posting and so on will be tried. If no `insert-entry` option
matches or none is given, the entry will be inserted at the end of the default
file.

---

## `auto-reload`

Default: `false`

Set this to `true` to make Fava automatically reload the page whenever a file
changes is detected. By default only a notification is shown which you can click
to reload the page. If the file change is due to user interaction, e.g.,
uploading a document or adding a transaction, Fava will always reload the page
automatically.

---

## `unrealized`

Default: `Unrealized`

The subaccount of the Equity account to post unrealized gains to if the account
trees are shown at market value.

---

## `currency-column`

Default: `61`

This option can be used to configure how posting lines are aligned when saved to
file or when using 'Align Amounts' in the editor. Fava tries to align so that
the currencies all occur in the given column. Also, Fava will show a vertical
line before this column in the editor.

---

## `sidebar-show-queries`

Default: `5`

The maximum number of queries to link to in the sidebar. Set this value to `0`
to hide the links altogether.

---

## `upcoming-events`

Default: `7`

Show a notification bubble in the sidebar displaying the number of events less
than `upcoming-events` days away. Set this value to `0` to disable this feature.

---

## `show-closed-accounts`

Default: `false`

## `show-accounts-with-zero-transactions`

Default: `true`

## `show-accounts-with-zero-balance`

Default: `true`

These three options specify which accounts (not) to show in the account trees,
like on the income statement. Accounts with a non-zero balance will always be
shown.

---

## `collapse-pattern`

Default: Not set

This option is used to specify accounts that will be collapsed in the displayed
account trees. The argument to this option is a regular expression matching
account names. This option can be specified multiple times.

Collapsing all accounts below a specific depth in the account tree can be
accomplished by a regex such as: `.*:.*:.*` (this example collapses all accounts
that are three levels deep).

---

## `use-external-editor`

Default: `false`

If `true`, instead of using the internal editor, the `beancount://` URL scheme
is used. See the
[Beancount urlscheme](https://github.com/aumayr/beancount_urlscheme) project for
details.

---

## `account-journal-include-children`

Default: `true`

This determines if the journal in the account report includes entries of
sub-accounts.

---

## `uptodate-indicator-grey-lookback-days`

Default: `60`

If there has been no activity in given number of days since the last balance
entry, then the grey uptodate-indicator is shown.

---

## `import-config`

Default: Not set

Path to a Beancount import configuration file. See the [Import](./import) help
page for details.

---

## `import-dirs`

Default: Not set

Set the directories to be scanned by the Beancount import mechanism.

---

## `invert-income-liabilities-equity`

Default: False

In Beancount the Income, Liabilities and Equity accounts tend to have a negative
balance (see
[Types of Accounts](https://beancount.github.io/docs/the_double_entry_counting_method.html#types-of-accounts)).

This Fava option flips the sign of these three accounts in the income statement
and the balance sheet. This way, the net profit chart will show positive numbers
if the income is greater than the expenses for a given timespan.

Note: To keep consistency with the internal accounting of beancount, the journal
and the individual account pages are not affected by this configuration option.

---

## `conversion-currencies`

Default: Not set

When set, the currency conversion select dropdown in all charts will show the
list of currencies specified in this option. By default, Fava lists all
operating currencies and those currencies that match ISO 4217 currency codes.
