To customize some of Fava's behaviour, you can add custom entries like the
following to your Beancount file.

<pre><textarea class="editor-readonly">
2016-06-14 custom "fava-option" "default-file"
2016-06-14 custom "fava-option" "interval" "week"
2016-04-14 custom "fava-option" "charts" "false"
2016-04-14 custom "fava-option" "journal-show" "transaction open"
2016-04-14 custom "fava-option" "editor-print-margin-column" "10" </textarea></pre>

Below is a list of all possible options for Fava.

---

## `language`

Default: Not set

Fava currently has an English (`en`), a German (`de`), a Russian (`ru`), a
Spanish (`es`), a Chinese (`zh`), a French (`fr`), a Dutch (`nl`) and a
Portuguese (`pt`) translation. If this setting is not specified, Fava will try
to guess the language from your browser settings.

---

## `default-file`

Use this option to specify a default file for the editor to open.  This option
takes no value, the file the custom entry is in will be used as the default.
If this option is not specified, Fava opens the main file by default.

---

## `interval`

Default: `month`

The default interval that charts and the account reports by interval use.
The possible options are `day`, `week`, `month`, `quarter`, and `year`.

---

## `charts`

Default: `true`

Set this to `false` to hide the charts. In any case, they can be hidden/shown
using the "Toggle Charts" button.

---

## `extensions`

Default: Not set.

A space-separated list of Python modules to load as extensions. The directory
of the main Beancount file is searched too, so for example a `my_extension.py`
right next to it could be used by giving `my_extension`. Note that Python has a
global namespace for currently loaded modules, so try avoiding simple names
that might coincide with some Python library (as well as running Fava on two
files that have different extensions of the same name).

---

## `insert-entry`

Default: Not set.

This option can be used to specify where entries are inserted. The argument to
this option should be a regular expression matching account names. This option
can be given multiple times. When adding an entry, the account of the entry
(for a transaction, the account of the last posting is used) is matched against
all `insert-entry` options and the entry will be inserted before the datewise
latest of the matching options. If the entry is a Transaction and no
`insert-entry` option matches the account of the last posting the account of
the second to last posting and so on will be tried. If no `insert-entry` option
matches or none is given, the entry will be inserted at the end of the main
file.

---

## `auto-reload`

Default: `false`.

Set this to `true` to make Fava automatically reload the page whenever a file
changes is detected. By default only a notification is shown which you can
click to reload the page.  If the file change is due to user interaction, e.g.,
uploading a document or adding a transaction, Fava will always reload the page
automatically.

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

## `upcoming-events`

Default: `7`

Show a notification bubble in the sidebar displaying the number of events less
than `upcoming-events` days away.
Set this value to `0` to disable this feature.

---

## `show-closed-accounts`

Default: `false`

This and the next two options specify which accounts (not) to show in the
account trees, like on the income statement.

---

## `show-accounts-with-zero-transactions`

Default: `true`

Like `show-closed-accounts`.

---

## `show-accounts-with-zero-balance`

Default: `true`

Like `show-closed-accounts`.

---

## `editor-print-margin-column`

Default: `60`

Show a vertical line after this column in the editor.
Can be used to keep decimal points aligned for example.

---

## `use-external-editor`

Default: `false`

If `true`, instead of using the internal editor, the `beancount://` URL scheme
is used. See the
[Beancount urlscheme](http://github.com/aumayr/beancount_urlscheme) project for
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

## `incognito`

Default: `false`

If set to `true` all digits will be replaced with "X".

---

## `import-config`

Default: Not set

Path to a Beancount import configuration file. See the [Import]({{
url_for('help_page', page_slug='import') }}) help page for details.

---

## `import-dirs`

Default: Not set

Set the directories to be scanned by the Beancount import mechanism.
