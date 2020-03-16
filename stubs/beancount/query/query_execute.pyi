# pylint: disable=all
# flake8: noqa
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple
from typing import NamedTuple

from beancount.core.data import Entries

def execute_query(query: Any, entries: Entries, options_map: Any): ...
