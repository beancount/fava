"""Custom Babel extractor for Svelte files."""

from __future__ import annotations

import re
from io import BytesIO
from typing import TYPE_CHECKING

from babel.messages.extract import extract_javascript

if TYPE_CHECKING:
    from collections.abc import Collection
    from collections.abc import Generator
    from collections.abc import Mapping

    from babel.messages.extract import _ExtractionResult
    from babel.messages.extract import _FileObj
    from babel.messages.extract import _JSOptions
    from babel.messages.extract import _Keyword


# The babel javascript extract function supports JSX and so also supports
# many parts of Svelte templates already.
# Svelte closing block tokens like {/if}, {/each}, {/await} confuse the
# JavaScript lexer: after a `{`, the `/` is treated as the start of a regex
# literal, causing the lexer to silently skip everything that follows.
# Replace them with empty JS blocks `{}` before extraction.
_SVELTE_CLOSE_BLOCK = re.compile(rb"\{/[a-z]+\}")


def extract_svelte(
    fileobj: _FileObj,
    keywords: Mapping[str, _Keyword],
    comment_tags: Collection[str],
    options: _JSOptions,
) -> Generator[_ExtractionResult, None, None]:
    """Extract messages from Svelte files."""
    contents = fileobj.read()
    contents = _SVELTE_CLOSE_BLOCK.sub(b"{}", contents)
    yield from extract_javascript(
        BytesIO(contents), keywords, comment_tags, options
    )
