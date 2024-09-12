import { sum } from "d3-array";

import { Amount, Position } from "../../entries";
import { collect } from "../../lib/result";
import type { ValidationT, Validator } from "../../lib/validation";
import {
  array,
  boolean,
  constant,
  constants,
  date,
  defaultValue,
  number,
  object,
  optional,
  record,
  string,
  tagged_union,
  unknown,
} from "../../lib/validation";
import { NumberColumn, StringColumn } from "../../sort";

const query_column_type = constants(
  "bool",
  "date",
  "int",
  "object",
  "set",
  "str",
  "Amount",
  "Decimal",
  "Inventory",
  "Position",
);

/** The query result data columns can have one of these various types. */
type QueryColumnType = ValidationT<typeof query_column_type>;

interface QueryType {
  dtype: QueryColumnType;
  name: string;
}

const query_type = object({
  dtype: query_column_type,
  name: string,
});

const query_table_raw = object({
  types: array(query_type),
  rows: array(array(unknown)),
});

const optional_number_record = optional(record(number));

export class Inventory {
  constructor(readonly value: Record<string, number>) {}

  static validator: Validator<Inventory> = (json) =>
    optional_number_record(json).map((v) => new Inventory(v ?? {}));
}

export type QueryCell =
  | null
  | Amount
  | boolean
  | Date
  | number
  | Inventory
  | Position
  | string[]
  | string;

class StringSortedQueryColumn<T> extends StringColumn<QueryCell[]> {
  dtype: QueryColumnType;
  constructor(
    type: QueryType,
    readonly index: number,
    readonly validator: Validator<T>,
    str_value_for_sorting: (v: T) => string,
  ) {
    super(type.name, (row) => str_value_for_sorting(row[index] as T));
    this.dtype = type.dtype;
  }
}

class NumberSortedQueryColumn<T> extends NumberColumn<QueryCell[]> {
  dtype: QueryColumnType;
  constructor(
    type: QueryType,
    readonly index: number,
    readonly validator: Validator<T>,
    num_value_for_sorting: (v: T) => number,
  ) {
    super(type.name, (row) => num_value_for_sorting(row[index] as T));
    this.dtype = type.dtype;
  }
}

function get_query_column(type: QueryType, index: number) {
  switch (type.dtype) {
    case "bool":
      return new StringSortedQueryColumn(type, index, boolean, (v) =>
        v.toString(),
      );
    case "date":
      return new NumberSortedQueryColumn(type, index, optional(date), (v) =>
        v == null ? 0 : +v,
      );
    case "int":
    case "Decimal":
      return new NumberSortedQueryColumn(
        type,
        index,
        optional(number),
        (v) => v ?? 0,
      );
    case "set":
      return new StringSortedQueryColumn(type, index, array(string), (v) =>
        v.join(","),
      );
    case "object":
    case "str":
      return new StringSortedQueryColumn(
        type,
        index,
        defaultValue(string, () => ""),
        (v) => v,
      );
    case "Amount":
      return new NumberSortedQueryColumn(
        type,
        index,
        Amount.validator,
        (v) => v.number,
      );
    case "Inventory":
      return new NumberSortedQueryColumn(
        type,
        index,
        Inventory.validator,
        (v) => sum(Object.values(v.value)),
      );
    case "Position":
      return new NumberSortedQueryColumn(
        type,
        index,
        Position.validator,
        (v) => v.units.number,
      );
    default:
      return type.dtype;
  }
}

type QueryColumn = ReturnType<typeof get_query_column>;

/** The parsed and validated result for a query table result. */
export interface QueryResultTable {
  readonly t: "table";
  readonly columns: QueryColumn[];
  readonly rows: QueryCell[][];
}

/** The parsed and validated result for a query text result. */
export interface QueryResultText {
  readonly t: "string";
  readonly contents: string;
}

export type QueryResult = QueryResultText | QueryResultTable;

export const query_table_validator: Validator<QueryResultTable> = (
  json: unknown,
) =>
  query_table_raw(json).and_then(({ types, rows }) => {
    const columns = types.map(get_query_column);
    const validators: Validator<QueryCell>[] = columns.map((c) => c.validator);

    const parsed_rows = collect(
      rows.map((row) =>
        collect(validators.map((validator, index) => validator(row[index]))),
      ),
    );

    return parsed_rows.map((r) => ({ t: "table", columns, rows: r }));
  });

export const query_validator: Validator<QueryResult> = tagged_union("t", {
  string: object({ t: constant("string"), contents: string }),
  table: query_table_validator,
});
