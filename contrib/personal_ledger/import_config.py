"""Import config for Fava, set with the `import-config` option."""

from __future__ import annotations

from personal_ledger.importers import BankImporter
from personal_ledger.importers import categorize

CONFIG = [
    BankImporter("Assets:Checking", "EUR"),
]

HOOKS = [categorize]
