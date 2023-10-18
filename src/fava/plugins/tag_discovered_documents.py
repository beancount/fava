"""Beancount plugin to tag discovered documents.

It looks through all Document entries that were added by Beancount
automatically through file discovery and adds the tag "#discovered".
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fava.beans.abc import Document
from fava.beans.helpers import replace
from fava.util.sets import add_to_set

if TYPE_CHECKING:  # pragma: no cover
    from fava.beans.abc import Directive
    from fava.beans.types import BeancountOptions
    from fava.helpers import BeancountError

__plugins__ = ["tag_discovered_documents"]


def tag_discovered_documents(
    entries: list[Directive],
    options_map: BeancountOptions,
) -> tuple[list[Directive], list[BeancountError]]:
    """Tag automatically added documents."""
    if not options_map["documents"]:  # pragma: no cover
        return entries, []

    for index, entry in enumerate(entries):
        if isinstance(entry, Document) and entry.meta["lineno"] == 0:
            entries[index] = replace(
                entry,
                tags=add_to_set(entry.tags, "discovered"),
            )

    return entries, []
