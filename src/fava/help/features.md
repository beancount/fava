# Fava's features

This is an overview of some of the more advanced features that Fava has to
offer.

## Editor

The [editor](../editor) provides a convenient way to edit the source file. If
you want to use a file different from the main file to be opened by default, use
the [`default-file`](./options#default-file) option. If you have
[`insert-entry`](./options#insert-entry) options set, the cursor will by default
jump to the (date-wise) latest one in the opened file.

The editor supports auto-completion for various entities, e.g., account names,
payees, and tags. Trailing whitespace is highlighted in red. The Tab key in the
editor can be used for indentation - to escape this keyboard trap, press Escape
and then Tab directly after it.

## Queries

On the [Query](../query/) report you can execute queries like with the
`bean-query` command-line tool. For an explanation of how these queries work see
the [Beancount Query Language Reference](http://furius.ca/beancount/doc/query).

Fava displays charts for BQL queries - if they have exactly two columns like the
following example with the first being a date or string and the second an
inventory, then a line chart or treemap chart is shown on the query page.

```
SELECT
    payee,
    SUM(COST(position)) AS balance
WHERE
    account ~ 'Expenses'
GROUP BY payee, account
```

Fava supports downloading the result of these queries in various file formats.
By default, only exporting to `csv` is supported. For support of `xlsx` and
`ods`, install Fava with the `excel` feature:

```
pip3 install fava[excel]
```

## Adding Transactions

By clicking the `+` button or using the `n` keyboard shortcut you can open a
form to insert a transaction to your Beancount file. The position that
transactions are inserted at can be specified in a flexible way using the
[`insert-entry`](./options#insert-entry) option. If you want to set a bookmark
to this form, adding `#add-transaction` to any URL in Fava will open it on load.
Tags and links can be added in the form by adding them (separated by spaces) to
the narration field, e.g., `narration #tag ^somelink`.

## Up-to-date indicators

Fava offers colored indicators that can help you keep your accounts up-to-date.
They are shown next to accounts that have the metadata
`fava-uptodate-indication: TRUE` set on their Open directive. The colors have
the following meaning:

- green: The last entry for this account is a balance check that passed.
- red: The last entry is a balance check that failed.
- yellow: The last entry is not a balance check.

In addition, a grey dot will be shown if the account has not been updated in a
while, as configured by the `uptodate-indicator-grey-lookback-days` option.

## Displaying only relevant accounts

To help display only the most relevant subset of accounts when managing a large
number or a deep hierarchy of accounts, Fava offers the following options:

- `show-closed-accounts`
- `show-accounts-with-zero-balance`
- `show-accounts-with-zero-transactions`
- `collapse-pattern`

## Opening an external editor

Fava can open up your source file in your favorite editor directly from the web
interface using the `use-external-editor` configuration variable through the
`beancount://` URL handler. See the
[Beancount urlscheme](https://github.com/aumayr/beancount_urlscheme) project for
pre-configured URL handlers for macOS and Cygwin.

## Multiple Beancount files

When you start Fava specifying multiple Beancount files, you can click the
Beancount file name on the top left to switch between the files.

## Custom links in the sidebar

If you regularly use certain views in Fava with different filters, you can put
links to them in the sidebar. Custom links can be put in the Beancount file,
utilizing the `custom` directive:

```
2016-05-04 custom "fava-sidebar-link" "Income 2014" "../income_statement?time=2014"
```

`"fava-sidebar-link"` specifies that this directive is for a custom sidebar
link, followed by the title to display in the sidebar (`"Income 2014"` in this
example), and finally the URL to link to. The URL can be relative, like in the
example above, or absolute, even linking to an external site.

Two frequently used custom links are for showing all Documents and all Notes
found in the journal:

- For all Documents: `/<slug>/journal/?show=document`
- For all Notes: `/<slug>/journal/?show=note`

There is a special URL handler `/jump` which can be used to jump to the current
page with given URL parameters. For example, `/jump?time=month` will show the
current page but change the time filter to the current month.

## Language

You can change the language of the interface by specifying the
[`language`](./options#language) option. If no option is specified, Fava tries
to guess the language from your browser settings.

## Documents upload

One or more documents can be uploaded by drag and drop on account names or
Journal rows.

### Uploading documents

To store a document in a specific account, just drag and drop the file on the
account name in a tree-table.

While still dragging, the background-color of the account name will switch to
blue, indicating that you can drop a file there.

Once dropped, a popup will be shown where you can rename the file before
storing. If the filename does not already start with a date (`YYYY-MM-DD`), the
current date will be added as a prefix automatically.

The file will be then stored in your Beancount documents folder, in a sub-folder
named after the account. You can set the path to the Beancount documents folder
by specifying the `option "documents" "/Users/test/invoices"`-option (absolute
or relative to your Beancount file) in your Beancount file.

Beancount will automatically discover files in your `"documents"`-folders and
generate Document entries for them.

When enabling the `tag_discovered_documents`-plugin, these Document entries will
be tagged with `#discovered` and can be filtered in the Journal:

```
plugin "fava.plugins.tag_discovered_documents"
```

### Uploading statements

When dropping a file on a transaction (or one of its postings) in the Journal,
the file will be uploaded as described above, and a `document`-metadata-entry
inserted for the transaction in your Beancount file.

When dropped on the description the subfolder corresponds to the account of the
first posting.

**Note**: Uploading statements modifies your Beancount file!

When enabling the `link_documents`-plugin, the Document entries created by
Beancount (see above) will be tagged with `#linked`, linked to the corresponding
transaction and can be filtered in the Journal:

```
plugin "fava.plugins.link_documents"
```

### Exporting

The entries that are currently shown in Fava, with filters applied, can be
downloaded in Beancount format by clicking the ⬇ (Export) button in the sidebar.
