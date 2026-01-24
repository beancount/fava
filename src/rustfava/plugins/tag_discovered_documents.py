"""Beancount plugin to tag discovered documents.

It looks through all Document entries that were added by Beancount
automatically through file discovery and adds the tag "#discovered".
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rustfava.beans.abc import Document
from rustfava.beans.helpers import replace
from rustfava.util.sets import add_to_set

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterator
    from collections.abc import Sequence

    from rustfava.beans.abc import Directive
    from rustfava.beans.types import BeancountOptions
    from rustfava.helpers import BeancountError

__plugins__ = ["tag_discovered_documents"]


def tag_discovered_documents(
    entries: Sequence[Directive],
    options_map: BeancountOptions,
) -> tuple[Sequence[Directive], list[BeancountError]]:
    """Tag automatically added documents."""
    if not options_map["documents"]:  # pragma: no cover
        return entries, []

    def _tag_discovered() -> Iterator[Directive]:
        for entry in entries:
            if isinstance(entry, Document) and entry.meta["lineno"] == 0:
                yield replace(
                    entry,
                    tags=add_to_set(entry.tags, "discovered"),
                )
            else:
                yield entry

    return list(_tag_discovered()), []
