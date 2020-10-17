import { todayAsString } from "./format";
import {
  array,
  constant,
  object,
  optional_string,
  record,
  string,
  union,
  unknown,
  Validator,
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

export type EntryTypeName = "Balance" | "Note" | "Transaction";

abstract class EntryBase {
  type: EntryTypeName;

  date: string;

  meta: Record<string, unknown>;

  constructor(type: EntryTypeName) {
    this.type = type;
    this.meta = {};
    this.date = todayAsString();
  }
}

const validatorBase = {
  type: string,
  date: string,
  meta: record(unknown),
};

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

  postings: Posting[];

  constructor() {
    super("Transaction");
    this.flag = "*";
    this.payee = "";
    this.narration = "";
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
