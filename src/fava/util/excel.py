"""Writing query results to CSV and spreadsheet documents."""

from __future__ import annotations

import csv
import datetime
import io
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

    from beanquery import Column

    ResultRow = tuple[Any, ...]

try:
    # since this is a conditional dependency, there will be different mypy
    # errors depending on whether it's installed
    import pyexcel  # type: ignore  # noqa: PGH003

    HAVE_EXCEL = True
except ImportError:  # pragma: no cover
    HAVE_EXCEL = False


class InvalidResultFormatError(ValueError):  # noqa: D101
    def __init__(self, result_format: str) -> None:  # pragma: no cover
        super().__init__(f"Invalid result format: {result_format}")


def to_excel(
    types: list[Column],
    rows: list[ResultRow],
    result_format: str,
    query_string: str,
) -> io.BytesIO:
    """Save result to spreadsheet document.

    Args:
        types: query result_types.
        rows: query result_rows.
        result_format: 'xlsx' or 'ods'.
        query_string: The query string (is written to the document).

    Returns:
        The (binary) file contents.
    """
    if result_format not in {"xlsx", "ods"}:  # pragma: no cover
        raise InvalidResultFormatError(result_format)
    resp = io.BytesIO()
    book = pyexcel.Book({
        "Results": _result_array(types, rows),
        "Query": [["Query"], [query_string]],
    })
    book.save_to_memory(result_format, resp)
    resp.seek(0)
    return resp


def to_csv(types: list[Column], rows: list[ResultRow]) -> io.BytesIO:
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


def _result_array(
    types: list[Column],
    rows: list[ResultRow],
) -> list[list[str]]:
    result_array = [[t.name for t in types]]
    result_array.extend(_row_to_pyexcel(row, types) for row in rows)
    return result_array


def _row_to_pyexcel(row: ResultRow, header: list[Column]) -> list[str]:
    result = []
    for idx, column in enumerate(header):
        value = row[idx]
        if not value:
            result.append(value)
            continue
        type_ = column.datatype
        if type_ is Decimal:
            result.append(float(value))
        elif type_ is int:
            result.append(value)
        elif type_ is set:
            result.append(" ".join(value))
        elif type_ is datetime.date:
            result.append(str(value))
        else:
            if not isinstance(value, str):  # pragma: no cover
                msg = f"unexpected type {type(value)}"
                raise TypeError(msg)
            result.append(value)
    return result
