"""Batch editor extension for Fava.

This is a simple batch editor that allows a batch of 20 entries
retrieved with a BQL query to be edited on the same page

There is currently a limitation where each entry needs to be saved
individually
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from fava.beans.abc import Transaction
from fava.beans.funcs import hash_entry
from fava.context import g
from fava.core.file import get_entry_slice
from fava.ext import FavaExtensionBase
from fava.helpers import FavaAPIError

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive


class BatchEdit(FavaExtensionBase):
    """Extension page that allows basic batch editing of entries."""

    report_title = "Batch Editor"

    has_js_module = True

    def get_entries(self, entry_hashes: list[str]) -> dict[str, Directive]:
        """Find a set of entries.

        Arguments:
            entry_hashes: Hashes of the entries.

        Returns:
            A dictionary of { entry_id: entry } for each given entry hash that is found
        """
        entries_set = set(entry_hashes)
        hashed_entries = [(hash_entry(e), e) for e in g.filtered.entries]
        return {
            key: entry for key, entry in hashed_entries if key in entries_set
        }

    def source_slices(self, query: str) -> list[dict[str, str]]:
        contents, _types, rows = self.ledger.query_shell.execute_query(
            g.filtered.entries, f"SELECT distinct id WHERE {query}"
        )
        if contents and "ERROR" in contents:
            raise FavaAPIError(contents)

        transaction_ids = [row.id for row in rows]
        entries = self.get_entries(transaction_ids)
        results = []
        for tx_id in transaction_ids[:20]:
            entry = entries[tx_id]
            # Skip generated entries
            if isinstance(entry, Transaction) and entry.flag == "S":
                continue
            source_slice, sha256sum = get_entry_slice(entry)
            results.append(
                {
                    "slice": source_slice,
                    "entry_hash": tx_id,
                    "sha256sum": sha256sum,
                }
            )
        return results
