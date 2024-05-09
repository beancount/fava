import { day, type FormatterContext } from "./format";
import { is_empty } from "./lib/objects";
import { ok } from "./lib/result";
import type { SafeValidator, Validator } from "./lib/validation";
import {
  array,
  constant,
  date,
  defaultValue,
  number,
  object,
  optional,
  optional_string,
  record,
  string,
  tagged_union,
} from "./lib/validation";

const entry_meta_item: SafeValidator<string | number | boolean> = (json) => {
  if (
    typeof json == "boolean" ||
    typeof json == "number" ||
    typeof json == "string"
  ) {
    return ok(json);
  }
  return ok("Unsupported metadata value");
};

const entry_meta_validator = record(entry_meta_item);

/** An amount is a pair of number and currency. */
export class Amount {
  constructor(
    readonly number: number,
    readonly currency: string,
  ) {}

  /** Render to a string. */
  str($ctx: FormatterContext): string {
    return $ctx.amount(this.number, this.currency);
  }

  private static raw_validator = object({ number, currency: string });

  static validator: Validator<Amount> = (json) =>
    Amount.raw_validator(json).map(
      ({ number, currency }) => new Amount(number, currency),
    );
}

/** A cost is a pair of number and currency with date and an optional label. */
export class Cost {
  constructor(
    readonly number: number,
    readonly currency: string,
    readonly date: Date | null,
    readonly label: string | null,
  ) {}

  /** Render to a string. */
  str($ctx: FormatterContext): string {
    const strs = [$ctx.amount(this.number, this.currency)];
    if (this.date) {
      strs.push(day(this.date));
    }
    if (this.label != null && this.label) {
      strs.push(`"${this.label}"`);
    }
    return strs.join(", ");
  }

  private static raw_validator = object({
    number,
    currency: string,
    date: optional(date),
    label: optional_string,
  });

  static validator: Validator<Cost> = (json) =>
    Cost.raw_validator(json).map(
      ({ number, currency, date, label }) =>
        new Cost(number, currency, date, label),
    );
}

/** A position, a pair of units and cost. */
export class Position {
  constructor(
    readonly units: Amount,
    readonly cost: Cost | null,
  ) {}

  private static raw_validator = object({
    units: Amount.validator,
    cost: optional(Cost.validator),
  });

  static validator: Validator<Position> = (json) =>
    Position.raw_validator(json).map(
      ({ units, cost }) => new Position(units, cost),
    );
}

/** A posting. */
export class Posting {
  account: string;
  amount: string;
  meta: EntryMetadata;

  constructor() {
    this.account = "";
    this.amount = "";
    this.meta = {};
  }

  is_empty(): boolean {
    return !this.account && !this.amount && is_empty(this.meta);
  }

  private static raw_validator = object({
    account: string,
    amount: string,
    meta: defaultValue(entry_meta_validator, () => ({})),
  });

  static validator: Validator<Posting> = (json) =>
    Posting.raw_validator(json).map((value) =>
      Object.assign(new Posting(), value),
    );
}

export type EntryMetadata = Record<string, string | boolean | number>;
export type EntryTypeName =
  | "Balance"
  | "Document"
  | "Event"
  | "Note"
  | "Transaction";

const validatorBase = {
  t: string,
  date: string,
  meta: entry_meta_validator,
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
    this.meta = {};
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
  return e.meta.__duplicate__ === true;
}
