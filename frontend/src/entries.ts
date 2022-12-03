import { todayAsString } from "./format";
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

export const entryBaseValidator = object(validatorBase);
export interface EntryBaseAttributes {
  type: string;
  date: string;
  meta: EntryMetadata;
}

abstract class EntryBase {
  type: EntryTypeName;

  date: string;

  meta: EntryMetadata;

  constructor(type: EntryTypeName) {
    this.type = type;
    this.meta = {};
    this.date = todayAsString();
  }
}

export class Balance extends EntryBase {
  account: string;

  amount: Amount;

  constructor() {
    super("Balance");
    this.account = "";
    this.amount = {
      number: "",
      currency: "",
    };
  }

  static validator = object({
    ...validatorBase,
    type: constant("Balance"),
    account: string,
    amount: object({ number: string, currency: string }),
  });
}

export class Note extends EntryBase {
  account: string;

  comment: string;

  constructor() {
    super("Note");
    this.account = "";
    this.comment = "";
  }

  static validator = object({
    ...validatorBase,
    type: constant("Note"),
    account: string,
    comment: string,
  });
}

export class Transaction extends EntryBase {
  flag: string;

  payee: string;

  narration: string;

  tags: string[];

  links: string[];

  postings: Posting[];

  constructor() {
    super("Transaction");
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

  static validator = object({
    ...validatorBase,
    type: constant("Transaction"),
    flag: string,
    payee: optional_string,
    narration: optional_string,
    tags: array(string),
    links: array(string),
    postings: array(postingValidator),
  });

  static fromJSON(json: unknown): Transaction {
    return Object.assign(new Transaction(), Transaction.validator(json));
  }
}

export type Entry = Balance | Note | Transaction;

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

export function create(type: EntryTypeName): Entry {
  return new constructors[type]();
}

/**
 * Check whether the given entry is marked as duplicate (used in imports).
 */
export function isDuplicate(e: Entry): boolean {
  return !!e.meta.__duplicate__;
}
