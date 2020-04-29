import { todayAsString } from "./format";
import { array, object, string, constant, record } from "./lib/validation";

interface Posting {
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

abstract class EntryBase {
  type: string;

  date: string;

  meta: Record<string, string>;

  constructor(type: string) {
    this.type = type;
    this.meta = {};
    this.date = todayAsString();
  }
}

const validatorBase = {
  type: string,
  date: string,
  meta: record(string),
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
}

export class Note extends EntryBase {
  account: string;

  comment: string;

  constructor() {
    super("Note");
    this.account = "";
    this.comment = "";
  }
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
    payee: string,
    narration: string,
    postings: array(postingValidator),
  });

  static fromJSON(json: unknown): Transaction {
    return Object.assign(new Transaction(), Transaction.validator(json));
  }
}

export type Entry = Balance | Note | Transaction;
