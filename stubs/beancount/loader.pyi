# pylint: disable=all
# flake8: noqa
from collections import namedtuple
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

from beancount.core.data import Entries

def compute_input_hash(filenames: List[str]) -> str: ...
def run_transformations(
    entries: Entries, parse_errors: Any, options_map: Any, log_timings: Any
) -> Tuple[Entries, List[Any]]: ...
def _load(
    sources: List[Tuple[str, bool]],
    log_timings: Any,
    extra_validations: Any,
    encoding: Optional[str],
) -> Tuple[Entries, List[Any], Any]: ...
def load_file(source: str) -> Tuple[Entries, List[Any], Any]: ...
