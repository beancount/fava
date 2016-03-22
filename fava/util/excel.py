# -*- coding: utf-8 -*-

import csv
from collections import OrderedDict
import io

try:
    import pyexcel
    import pyexcel.ext.xls
    import pyexcel.ext.xlsx
    import pyexcel.ext.ods3
    HAVE_EXCEL = True
except ImportError:
    HAVE_EXCEL = False


def to_excel(types, rows, result_format, query_string):
    assert result_format in ('xls', 'xlsx', 'ods')
    respIO = io.BytesIO()
    book = pyexcel.Book(OrderedDict([
        ('Results', _result_array(types, rows)),
        ('Query',   [['Query'], [query_string]])
    ]))
    book.save_to_memory(result_format, respIO)
    respIO.seek(0)
    return respIO


def to_csv(types, rows):
    respIO = io.StringIO()
    result_array = _result_array(types, rows)
    csv.writer(respIO).writerows(result_array)
    return io.BytesIO(respIO.getvalue().encode('utf-8'))


def _result_array(types, rows):
    result_array = [[name for name, t in types]]
    for row in rows:
        result_array.append(_row_to_pyexcel(row, types))
    return result_array


def _row_to_pyexcel(row, header):
    result = []
    for idx, column in enumerate(header):
        value = row[idx]
        if not value:
            result.append(value)
            continue
        type_ = column[1]
        if str(type_) == "<class 'decimal.Decimal'>":
            result.append(float(value))
        elif str(type_) == "<class 'int'>":
            result.append(int(value))
        else:
            result.append(str(value))
    return result
