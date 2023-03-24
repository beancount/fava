import { ok } from "./lib/result";
import type { Validator } from "./lib/validation";
import {
  array,
  boolean,
  constant,
  defaultValue,
  number,
  object,
  optional_string,
  record,
  string,
  union,
} from "./lib/validation";

export interface Posting {
  account: string;
  amount: string;
}

const postingValidator = object({
  account: string,
  amount: string,
});

interface Amount {
  number: string;
  currency: string;
}

export function emptyPosting(): Posting {
  return {
    account: "",
    amount: "",
  };
}

export type EntryMetadata = Record<string, string | boolean | number>;
export type EntryTypeName = "Balance" | "Note" | "Transaction";

const entry_meta_validator = record(
  defaultValue(union(boolean, number, string), "Unsupported metadata value")
);

const validatorBase = {
  type: string,
  date: string,
  meta: entry_meta_validator,
};

export interface EntryBaseAttributes {
  type: string;
  date: string;
  meta: EntryMetadata;
}

export const entryBaseValidator = object(
  validatorBase
) satisfies Validator<EntryBaseAttributes>;

abstract class EntryBase {
  type: EntryTypeName;

  date: string;

  meta: EntryMetadata;

  constructor(type: EntryTypeName, date: string) {
    this.type = type;
    this.meta = {};
    this.date = date;
  }
}

export class Balance extends EntryBase {
  account: string;

  amount: Amount;

  constructor(date: string) {
    super("Balance", date);
    this.account = "";
    this.amount = {
      number: "",
      currency: "",
    };
  }

  private static raw_validator = object({
    ...validatorBase,
    type: constant("Balance"),
    account: string,
    amount: object({ number: string, currency: string }),
  });

  static validator: Validator<Balance> = (json) => {
    const res = Balance.raw_validator(json);
    return res.success
      ? ok(Object.assign(new Balance(res.value.date), res.value))
      : res;
  };
}

export class Note extends EntryBase {
  account: string;

  comment: string;

  constructor(date: string) {
    super("Note", date);
    this.account = "";
    this.comment = "";
  }

  private static raw_validator = object({
    ...validatorBase,
    type: constant("Note"),
    account: string,
    comment: string,
  });

  static validator: Validator<Note> = (json) => {
    const res = Note.raw_validator(json);
    return res.success
      ? ok(Object.assign(new Note(res.value.date), res.value))
      : res;
  };
}

export class Transaction extends EntryBase {
  flag: string;

  payee: string;

  narration: string;

  tags: string[];

  links: string[];

  postings: Posting[];

  constructor(date: string) {
    super("Transaction", date);
    this.flag = "*";
    this.payee = "";
    this.narration = "";
    this.tags = [];
    this.links = [];
    this.postings = [emptyPosting(), emptyPosting()];
  }

  toString(): string {
    const postings = this.postings.map((p) => `  ${p.account}  ${p.amount}`);
    return (
      `${this.date} ${this.flag} "${this.payee}" "${this.narration}"` +
      `\n${postings.join("\n")}`
    );
  }

  static raw_validator = object({
    ...validatorBase,
    type: constant("Transaction"),
    flag: string,
    payee: optional_string,
    narration: optional_string,
    tags: array(string),
    links: array(string),
    postings: array(postingValidator),
  });

  static validator: Validator<Transaction> = (json) => {
    const res = Transaction.raw_validator(json);
    return res.success
      ? ok(Object.assign(new Transaction(res.value.date), res.value))
      : res;
  };
}

/** A Beancount entry, currently only support Balance, Note, and Transaction. */
export type Entry = Balance | Note | Transaction;

/** Validate an Entry. */
export const entryValidator: Validator<Entry> = union(
  Balance.validator,
  Note.validator,
  Transaction.validator
);

const constructors = {
  Balance,
  Note,
  Transaction,
};

/**
 * Create an empty entry of given type on the given day.
 */
export function create(type: EntryTypeName, date: string): Entry {
  return new constructors[type](date);
}

/**
 * Check whether the given entry is marked as duplicate (used in imports).
 */
export function isDuplicate(e: Entry): boolean {
  return !!e.meta.__duplicate__;
}
