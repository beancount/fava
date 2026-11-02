"""Example Beancount plugin.

Enable it in your ledger with::

    plugin "personal_ledger"
"""

from __future__ import annotations

from typing import Any

__plugins__ = ["example_plugin"]


def example_plugin(
    entries: list[Any],
    options_map: dict[str, Any],  # noqa: ARG001
) -> tuple[list[Any], list[Any]]:
    """Return the entries unchanged - modify them here as needed."""
    return entries, []
