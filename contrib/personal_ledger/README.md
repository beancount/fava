This is an example of how `uv` can be used to set up Fava in a project folder,
easily allowing adding more dependencies and writing personal importers and
plugins.

The package in `src/personal_ledger` is installed into the project's virtual
environment, so modules in it can be used directly from your ledger, for example
the plugin in `__init__.py` with `plugin "personal_ledger"`. The CSV importer in
`importers.py` is set up in `import_config.py`, which the ledger points to with
the `import-config` option, together with an import hook that adds the balancing
posting for known payees.

To try it out, run `uv run fava ledger.beancount` in this folder, which starts
Fava on the included example ledger. The import page then offers to import the
example CSV file in `downloads`.
