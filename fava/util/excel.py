# -*- coding: utf-8 -*-

import io

from collections import OrderedDict

import pyexcel
import pyexcel.ext.xls
import pyexcel.ext.xlsx
import pyexcel.ext.ods3


class FavaExcel:
    def __init__(self, results, error):
        if results:
            self.currencies_from_inventory(results)
            self.result_array = []
            self.result_array.append(self.header_to_pyexcel(results[0]))
            for row in results[1]:
                self.result_array.append(self.row_to_pyexcel(row, results[0]))
        else:
            self.result_array = [[error]]

    def save(self, result_format, query):
        if result_format in ('xls', 'xlsx', 'ods'):
            book = pyexcel.Book(OrderedDict([
                ('Results', self.result_array),
                ('Query',   [['Query'], [query]])
            ]))
            respIO = io.BytesIO()
            book.save_to_memory(result_format, respIO)
        else:
            respIO = pyexcel.save_as(array=self.result_array,
                                     dest_file_type=result_format)
        return respIO

    def currencies_from_inventory(self, results):
        self.currencies = {}
        for idx, column in enumerate(results[0]):
            if str(column[1]) == \
                    "<class 'beancount.core.inventory.Inventory'>":
                self.currencies[idx] = OrderedDict()
        for row in results[1]:
            for idx in self.currencies.keys():
                for value in row[idx].cost():
                    self.currencies[idx][value.units.currency] = None

    def row_to_pyexcel(self, row, header):
        result = []
        for idx, column in enumerate(header):
            type_ = column[1]
            value = row[idx]
            if str(type_) == "<class 'beancount.core.position.Position'>":
                result.append(float(value.units.number))
                result.append(value.units.currency)
            elif str(type_) == "<class 'beancount.core.inventory.Inventory'>":
                for currency in self.currencies[idx]:
                    number = 0.0
                    for position in value.cost():
                        if position.units.currency == currency:
                            number = float(position.units.number)
                    result.append(float(number))
                    result.append(str(currency))
            elif str(type_) == "<class 'decimal.Decimal'>":
                result.append(float(value))
            elif str(type_) == "<class 'int'>":
                result.append(int(value))
            else:
                result.append(str(value))
        return result

    def header_to_pyexcel(self, header):
        result = []
        for idx, column in enumerate(header):
            name, type_ = column
            if str(type_) == "<class 'beancount.core.position.Position'>":
                result.append("{} {}".format(name, "amount"))
                result.append("{} {}".format(name, "currency"))
            elif str(type_) == "<class 'beancount.core.inventory.Inventory'>":
                for currency in self.currencies[idx]:
                    result.append("{} {}".format(name, "amount"))
                    result.append("{} {}".format(name, currency))
            else:
                result.append(name)
        return result
