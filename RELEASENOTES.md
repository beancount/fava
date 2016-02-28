# Release notes for `fava`

## v0.2.5
*2016-02-28*

### Fixes

- Removed unused draft code.

## v0.2.4
*2016-02-28*

### Additions

- Added missing Holdings views compared to `bean-web` (Thanks @yagebu!).
- Custom queries are now shown in sidebar (Thanks @corani!).
- The user settings file is now editable in Source editor.
- Added second theme (Thanks Rubén Gómez!).
- Added Help pages.
- Query results can now be downloaded as CSV, XLS, XLSX and ODS.
- Documents can now be uploaded by dragging and dropping files over an Account
  name (Account view and all tree-tables).

### Removals

- The `uptodate-indicator-exclude-accounts` configuration option is gone. This
  should be configured via the Account metadata.

### Changes

- Speedier Journal rendering (Thanks @yagebu!).
- Only basenames will be shown for documents in the Journal (Thanks @corani!).
- Updated how up-to-date-indicators are calculated and displayed.
- Slightly reordered the sidebar menu.
- Minor UI tweaks.

### Fixes

- Fixed Net worth calculation (Thanks @yagebu!).
- Many small bug fixes.

### New configuration options

- `sidebar-show-queries`: The maximum number of custom queries to show in the
  sidebar (default: 5).
- `theme`: The theme to use. Valid themes are `"default"` and `"alternative"`
  (default: `"default"`).
- `editor-print-margin-column`: Set the column for the print margin in the
  Source editor (default: 60).

---
*(No release notes prior to v0.2.4)*
