---
title: Settings
---

To customize some of Fava's settings, pass the path to your settings file to
Fava using `fava --settings [path]`.  The settings file follows a syntax
similar to Windows INI files, like the following example:

```
[fava]
interval = week
journal-show = transaction balance note document
show-closed-accounts = True
sidebar-show-queries = 0
```

Below is a list of all possible settings for Fava.

---

## `theme`

Default: `default`

Fava currently ships two themes: "default" and "alternative".

---

## `language`

Default: Not set

Fava has an English (`en`) and a German (`de`) translation currently. If
this setting is not specified, Fava will try to guess the language from your
browser settings.

---

## `interval`

Default: `month`

The default interval that charts and the account reports by interval use.
The possible options are `day`, `week`, `month`, `quarter`, and `year`.

---

## `charts`

Default: `True`

Set this to `False` to hide the charts. In any case, they can be hidden/shown
using the "Toggle Charts" button.

---

## `journal-show`

Default: `transaction balance note document custom budget`

The entry types given in this list will be shown in the Journal report.
All other types will be hidden and can be toggled using the buttons.

---

## `journal-show-transaction`

Default: `cleared pending`

Similarly to the `journal-show` setting, this determines the transaction types
that will be shown in the Journal report. The "transaction types" correspond to
the following transaction flags:

- `cleared` - `*`
- `pending` - `!`
- `other` - All other transaction flags.

---

## `sidebar-show-queries`

Default: `5`

The maximum number of queries to link to in the sidebar.
Set this value to `0` to hide the links altogether.

---

## `show-closed-accounts`

Default: `False`

This and the next two options specify which accounts (not) to show in the
account trees, like on the income statement.

---

## `show-accounts-with-zero-transactions`

Default: `True`

Like `show-closed-accounts`.

---

## `show-accounts-with-zero-balance`

Default: `True`

Like `show-closed-accounts`.

---

## `editor-print-margin-column`

Default: `60`

Show a vertical line after this column in the editor.
Can be used to keep decimal points aligned for example.

---

## `editor-strip-trailing-whitespace`

Default: `False`

If set, strip all trailing whitespace when saving in Fava's editor.

---

## `editor-insert-marker`

Default: Not set

If present the cursor will be positioned above the specified insert marker.

---

## `use-external-editor`

Default: `False`

If `True`, instead of using the internal editor, the `beancount://` URL scheme
is used. See the
[beancount_urlscheme](http://github.com/aumayr/beancount_urlscheme) project for
details.

---

## `account-journal-include-children`

Default: `True`

This determines if the journal in the account report includes entries of
sub-accounts.

---

## `uptodate-indicator-grey-lookback-days`

Default: `60`

If there has been no activity in given number of days since the last balance
entry, then the grey uptodate-indicator is shown.
