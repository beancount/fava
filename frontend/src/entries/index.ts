import type { Validator } from "../lib/validation";
import {
  array,
  constant,
  defaultValue,
  object,
  optional_string,
  string,
  tagged_union,
} from "../lib/validation";
import { Amount } from "./amount";
import { Cost } from "./cost";
import { EntryMetadata } from "./metadata";
import { Position } from "./position";

export { Amount, Cost, EntryMetadata, Position };

/** A posting. */
export class Posting {
  account: string;
  amount: string;
  meta: EntryMetadata;

  constructor() {
    this.account = "";
    this.amount = "";
    this.meta = new EntryMetadata();
  }

  is_empty(): boolean {
    return !this.account && !this.amount && this.meta.is_empty();
  }

  private static raw_validator = object({
    account: string,
    amount: string,
    meta: defaultValue(EntryMetadata.validator, () => new EntryMetadata()),
  });

  static validator: Validator<Posting> = (json) =>
    Posting.raw_validator(json).map((value) =>
      Object.assign(new Posting(), value),
    );
}
export type EntryTypeName =
  | "Balance"
  | "Document"
  | "Event"
  | "Note"
  | "Transaction";

const validatorBase = {
  t: string,
  date: string,
  meta: EntryMetadata.validator,
};

/** The properties that all entries share. */
export interface EntryBaseAttributes {
  t: string;
  date: string;
  meta: EntryMetadata;
}

export const entryBaseValidator = object(
  validatorBase,
) satisfies Validator<EntryBaseAttributes>;

abstract class EntryBase {
  t: EntryTypeName;

  date: string;

  meta: EntryMetadata;

  constructor(type: EntryTypeName, date: string) {
    this.t = type;
    this.meta = new EntryMetadata();
    this.date = date;
  }
}

/** A balance. */
export class Balance extends EntryBase {
  account: string;

  amount: {
    number: string;
    currency: string;
  };

  constructor(date: string) {
    super("Balance", date);
    this.account = "";
    this.amount = { number: "", currency: "" };
  }

  private static raw_validator = object<Balance>({
    ...validatorBase,
    t: constant("Balance"),
    account: string,
    amount: object({ number: string, currency: string }),
  });

  static validator: Validator<Balance> = (json) =>
    Balance.raw_validator(json).map((value) =>
      Object.assign(new Balance(value.date), value),
    );
}

/** A document. */
export class Document extends EntryBase {
  readonly account: string;

  readonly filename: string;

  constructor(date: string) {
    super("Document", date);
    this.account = "";
    this.filename = "";
  }

  private static raw_validator = object<Document>({
    ...validatorBase,
    t: constant("Document"),
    account: string,
    filename: string,
  });

  static validator: Validator<Document> = (json) =>
    Document.raw_validator(json).map((value) =>
      Object.assign(new Document(value.date), value),
    );
}

/** An event. */
export class Event extends EntryBase {
  readonly type: string;

  readonly description: string;

  constructor(date: string) {
    super("Event", date);
    this.type = "";
    this.description = "";
  }

  private static raw_validator = object<Event>({
    ...validatorBase,
    t: constant("Event"),
    type: string,
    description: string,
  });

  static validator: Validator<Event> = (json) =>
    Event.raw_validator(json).map((value) =>
      Object.assign(new Event(value.date), value),
    );
}

/** A note. */
export class Note extends EntryBase {
  account: string;

  comment: string;

  constructor(date: string) {
    super("Note", date);
    this.account = "";
    this.comment = "";
  }

  private static raw_validator = object<Note>({
    ...validatorBase,
    t: constant("Note"),
    account: string,
    comment: string,
  });

  static validator: Validator<Note> = (json) =>
    Note.raw_validator(json).map((value) =>
      Object.assign(new Note(value.date), value),
    );
}

/** A transaction. */
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
    this.postings = [];
  }

  toString(): string {
    const postings = this.postings.map((p) => `  ${p.account}  ${p.amount}`);
    return (
      `${this.date} ${this.flag} "${this.payee}" "${this.narration}"` +
      `\n${postings.join("\n")}`
    );
  }

  toJSON(): this {
    return {
      // eslint-disable-next-line @typescript-eslint/no-misused-spread
      ...this,
      postings: this.postings.filter((p) => !p.is_empty()),
    };
  }

  private static raw_validator = object<
    Omit<Transaction, "toString" | "toJSON">
  >({
    ...validatorBase,
    t: constant("Transaction"),
    flag: string,
    payee: optional_string,
    narration: optional_string,
    tags: array(string),
    links: array(string),
    postings: array(Posting.validator),
  });

  static validator: Validator<Transaction> = (json) =>
    Transaction.raw_validator(json).map((value) =>
      Object.assign(new Transaction(value.date), value),
    );
}

/** A Beancount entry, currently only support Balance, Note, and Transaction. */
export type Entry = Balance | Document | Event | Note | Transaction;

/** Validate an Entry. */
export const entryValidator: Validator<Entry> = tagged_union("t", {
  Balance: Balance.validator,
  Document: Document.validator,
  Event: Event.validator,
  Note: Note.validator,
  Transaction: Transaction.validator,
});

/**
 * Check whether the given entry is marked as duplicate (used in imports).
 */
export function isDuplicate(e: Entry): boolean {
  const value = e.meta.get("__duplicate__");
  return value != null && value !== false;
}
