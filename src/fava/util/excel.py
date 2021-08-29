"""Writing query results to CSV and spreadsheet documents."""
import csv
import datetime
import io
from collections import OrderedDict
from typing import Any
from typing import List

from beancount.core.number import Decimal

try:
    import pyexcel  # type: ignore

    HAVE_EXCEL = True
except ImportError:  # pragma: no cover
    HAVE_EXCEL = False


def to_excel(
    types: Any, rows: Any, result_format: str, query_string: str
) -> Any:
    """Save result to spreadsheet document.

    Args:
        types: query result_types.
        rows: query result_rows.
        result_format: One of 'xls', 'xlsx', or 'ods'.
        query_string: The query string (is written to the document).

    Returns:
        The (binary) file contents.
    """
    assert result_format in ("xls", "xlsx", "ods")
    resp = io.BytesIO()
    book = pyexcel.Book(
        OrderedDict(
            [
                ("Results", _result_array(types, rows)),
                ("Query", [["Query"], [query_string]]),
            ]
        )
    )
    book.save_to_memory(result_format, resp)
    resp.seek(0)
    return resp


def to_csv(types: Any, rows: Any) -> Any:
    """Save result to CSV.

    Args:
        types: query result_types.
        rows: query result_rows.

    Returns:
        The (binary) file contents.
    """
    resp = io.StringIO()
    result_array = _result_array(types, rows)
    csv.writer(resp).writerows(result_array)
    return io.BytesIO(resp.getvalue().encode("utf-8"))


def _result_array(types: Any, rows: Any) -> Any:
    result_array = [[name for name, t in types]]
    for row in rows:
        result_array.append(_row_to_pyexcel(row, types))
    return result_array


def _row_to_pyexcel(row: Any, header: Any) -> List[str]:
    result = []
    for idx, column in enumerate(header):
        value = row[idx]
        if not value:
            result.append(value)
            continue
        type_ = column[1]
        if type_ == Decimal:
            result.append(float(value))
        elif type_ == int:
            result.append(value)
        elif type_ == set:
            result.append(" ".join(value))
        elif type_ == datetime.date:
            result.append(str(value))
        else:
            assert isinstance(value, str)
            result.append(value)
    return result
