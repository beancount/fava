import os
from collections.abc import Sequence
from typing import Any

from beancount.core import data
from beangulp import Importer

def extract_from_file(
    importer: Importer,
    filename: str | os.PathLike[str],
    existing_entries: Sequence[Any],
) -> data.Entries: ...
