import type { ValidationT, Validator } from "../lib/validation";
import {
  array,
  constant,
  defaultValue,
  object,
  optional,
  optional_string,
  string,
  tagged_union,
  unknown,
} from "../lib/validation";
import { Amount, RawAmount } from "./amount";
import { Cost } from "./cost";
import type { MetadataValue } from "./metadata";
import { EntryMetadata } from "./metadata";
import { Position } from "./position";

export { Amount, Cost, EntryMetadata, Position };

/** A posting. */
export class Posting {
  private constructor(
    readonly meta: EntryMetadata,
    readonly account: string,
    readonly amount: string,
  ) {}

  /** Create a new empty Posting. */
  static empty(): Posting {
    return new Posting(new EntryMetadata(), "", "");
  }

  is_empty(): boolean {
    return !this.account && !this.amount && this.meta.is_empty();
  }

  /** Set a property and return an updated copy. */
  set<T extends keyof Posting>(key: T, value: Posting[T]): Posting {
    const copy = new Posting(this.meta, this.account, this.amount);
    copy[key] = value;
    return copy;
  }

  private static raw_validator = object({
    meta: defaultValue(EntryMetadata.validator, () => new EntryMetadata()),
    account: string,
    amount: string,
  });

  static validator: Validator<Posting> = (json) =>
    Posting.raw_validator(json).map(
      ({ meta, account, amount }) => new Posting(meta, account, amount),
    );
}

/** The properties that all entries share. */
export interface EntryBaseAttributes {
  t: string;
  meta: EntryMetadata;
  date: string;
  entry_hash: string;
}

export const entryBaseValidator = object<EntryBaseAttributes>({
  t: string,
  meta: EntryMetadata.validator,
  date: string,
  entry_hash: string,
});

const string_array_validator = array(string);
const optional_string_array_validator = optional(string_array_validator);

abstract class EntryBase<T extends string> {
  constructor(
    readonly t: T,
    readonly meta: EntryMetadata,
    readonly date: string,
    readonly entry_hash: string,
  ) {}

  /** Clone. */
  clone(): this {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const copy: typeof this = Object.assign(
      // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
      Object.create(Object.getPrototypeOf(this)),
      this,
    );
    return copy;
  }

  /** Set a property and return an updated copy. */
  set<T extends keyof typeof this>(key: T, value: (typeof this)[T]): this {
    const copy = this.clone();
    copy[key] = value;
    return copy;
  }

  /** Set the value for a key and return an updated copy. */
  set_meta(key: string, value: MetadataValue): this {
    const copy = this.clone();
    // @ts-expect-error We can mutate it as we just created it and noone has access yet.
    copy.meta = this.meta.set(key, value);
    return copy;
  }

  /** Check whether the given entry is marked as duplicate (used in imports). */
  is_duplicate(): boolean {
    const value = this.meta.get("__duplicate__");
    return value != null && value !== false;
  }
}

/** A balance. */
export class Balance extends EntryBase<"Balance"> {
  private constructor(
    meta: EntryMetadata,
    date: string,
    entry_hash: string,
    readonly account: string,
    readonly amount: RawAmount,
  ) {
    super("Balance", meta, date, entry_hash);
  }

  /** Create a new empty Balance entry on the date. */
  static empty(date: string): Balance {
    return new Balance(new EntryMetadata(), date, "", "", RawAmount.empty());
  }

  private static raw_validator = object({
    t: constant("Balance"),
    meta: EntryMetadata.validator,
    date: string,
    entry_hash: string,
    account: string,
    amount: RawAmount.validator,
  });

  static validator: Validator<Balance> = (json) =>
    Balance.raw_validator(json).map(
      ({ date, meta, account, amount, entry_hash }) =>
        new Balance(meta, date, entry_hash, account, amount),
    );
}

/** A document. */
export class Document extends EntryBase<"Document"> {
  private constructor(
    meta: EntryMetadata,
    date: string,
    entry_hash: string,
    readonly account: string,
    readonly filename: string,
    readonly tags: string[] | null,
    readonly links: string[] | null,
  ) {
    super("Document", meta, date, entry_hash);
  }

  private static raw_validator = object({
    t: constant("Document"),
    meta: EntryMetadata.validator,
    date: string,
    entry_hash: string,
    account: string,
    filename: string,
    tags: optional_string_array_validator,
    links: optional_string_array_validator,
  });

  static validator: Validator<Document> = (json) =>
    Document.raw_validator(json).map(
      ({ date, meta, account, filename, entry_hash, tags, links }) =>
        new Document(meta, date, entry_hash, account, filename, tags, links),
    );
}

/** An event. */
export class Event extends EntryBase<"Event"> {
  private constructor(
    meta: EntryMetadata,
    date: string,
    entry_hash: string,
    readonly type: string,
    readonly description: string,
  ) {
    super("Event", meta, date, entry_hash);
  }

  private static raw_validator = object({
    t: constant("Event"),
    meta: EntryMetadata.validator,
    date: string,
    entry_hash: string,
    type: string,
    description: string,
  });

  static validator: Validator<Event> = (json) =>
    Event.raw_validator(json).map(
      ({ meta, date, entry_hash, type, description }) =>
        new Event(meta, date, entry_hash, type, description),
    );
}

/** A note. */
export class Note extends EntryBase<"Note"> {
  private constructor(
    meta: EntryMetadata,
    date: string,
    entry_hash: string,
    readonly account: string,
    readonly comment: string,
    readonly tags: string[] | null,
    readonly links: string[] | null,
  ) {
    super("Note", meta, date, entry_hash);
  }

  /** Create a new empty Note entry on the date. */
  static empty(date: string): Note {
    return new Note(new EntryMetadata(), date, "", "", "", null, null);
  }

  private static raw_validator = object({
    t: constant("Note"),
    meta: EntryMetadata.validator,
    date: string,
    entry_hash: string,
    account: string,
    comment: string,
    tags: optional_string_array_validator,
    links: optional_string_array_validator,
  });

  static validator: Validator<Note> = (json) =>
    Note.raw_validator(json).map(
      ({ meta, date, entry_hash, account, comment, tags, links }) =>
        new Note(meta, date, entry_hash, account, comment, tags, links),
    );
}

/** An Open entry. */
export class Open extends EntryBase<"Open"> {
  constructor(
    meta: EntryMetadata,
    date: string,
    entry_hash: string,
    readonly account: string,
    readonly currencies: string[] | null,
    readonly booking: string | null,
  ) {
    super("Open", meta, date, entry_hash);
  }

  private static raw_validator = object({
    t: constant("Open"),
    meta: EntryMetadata.validator,
    date: string,
    entry_hash: string,
    account: string,
    currencies: optional_string_array_validator,
    booking: optional(string),
  });

  static validator: Validator<Open> = (json) =>
    Open.raw_validator(json).map(
      ({ meta, date, entry_hash, account, currencies, booking }) =>
        new Open(meta, date, entry_hash, account, currencies, booking),
    );
}

/** A Close entry. */
export class Close extends EntryBase<"Close"> {
  constructor(
    meta: EntryMetadata,
    date: string,
    entry_hash: string,
    readonly account: string,
  ) {
    super("Close", meta, date, entry_hash);
  }

  private static raw_validator = object({
    t: constant("Close"),
    meta: EntryMetadata.validator,
    date: string,
    entry_hash: string,
    account: string,
  });

  static validator: Validator<Close> = (json) =>
    Close.raw_validator(json).map(
      ({ meta, date, entry_hash, account }) =>
        new Close(meta, date, entry_hash, account),
    );
}

/** A Price entry. */
export class Price extends EntryBase<"Price"> {
  constructor(
    meta: EntryMetadata,
    date: string,
    entry_hash: string,
    readonly currency: string,
    readonly amount: RawAmount,
  ) {
    super("Price", meta, date, entry_hash);
  }

  private static raw_validator = object({
    t: constant("Price"),
    meta: EntryMetadata.validator,
    date: string,
    entry_hash: string,
    currency: string,
    amount: RawAmount.validator,
  });

  static validator: Validator<Price> = (json) =>
    Price.raw_validator(json).map(
      ({ meta, date, entry_hash, currency, amount }) =>
        new Price(meta, date, entry_hash, currency, amount),
    );
}

/** A Pad entry. */
export class Pad extends EntryBase<"Pad"> {
  constructor(
    meta: EntryMetadata,
    date: string,
    entry_hash: string,
    readonly account: string,
    readonly source_account: string,
  ) {
    super("Pad", meta, date, entry_hash);
  }

  private static raw_validator = object({
    t: constant("Pad"),
    meta: EntryMetadata.validator,
    date: string,
    entry_hash: string,
    account: string,
    source_account: string,
  });

  static validator: Validator<Pad> = (json) =>
    Pad.raw_validator(json).map(
      ({ meta, date, entry_hash, account, source_account }) =>
        new Pad(meta, date, entry_hash, account, source_account),
    );
}

/** A Query entry. */
export class Query extends EntryBase<"Query"> {
  constructor(
    meta: EntryMetadata,
    date: string,
    entry_hash: string,
    readonly name: string,
    readonly query_string: string,
  ) {
    super("Query", meta, date, entry_hash);
  }

  private static raw_validator = object({
    t: constant("Query"),
    meta: EntryMetadata.validator,
    date: string,
    entry_hash: string,
    name: string,
    query_string: string,
  });

  static validator: Validator<Query> = (json) =>
    Query.raw_validator(json).map(
      ({ meta, date, entry_hash, name, query_string }) =>
        new Query(meta, date, entry_hash, name, query_string),
    );
}

/** A Custom entry. */
export class Custom extends EntryBase<"Custom"> {
  constructor(
    meta: EntryMetadata,
    date: string,
    entry_hash: string,
    readonly type: string, // This is the custom directive type string
    readonly values: unknown[],
  ) {
    super("Custom", meta, date, entry_hash);
  }

  private static raw_validator = object({
    t: constant("Custom"),
    meta: EntryMetadata.validator,
    date: string,
    entry_hash: string,
    type: string,
    values: array(unknown),
  });

  static validator: Validator<Custom> = (json) =>
    Custom.raw_validator(json).map(
      ({ meta, date, entry_hash, type, values }) =>
        new Custom(meta, date, entry_hash, type, values),
    );
}

const TAGS_RE = /(?:^|\s)#([A-Za-z0-9\-_/.]+)/g;
const LINKS_RE = /(?:^|\s)\^([A-Za-z0-9\-_/.]+)/g;

/** A transaction. */
export class Transaction extends EntryBase<"Transaction"> {
  private constructor(
    meta: EntryMetadata,
    date: string,
    entry_hash: string,
    readonly flag: string,
    readonly payee: string,
    readonly narration: string,
    readonly tags: string[],
    readonly links: string[],
    readonly postings: readonly Posting[],
  ) {
    super("Transaction", meta, date, entry_hash);
  }

  /** Create a new empty Transaction entry on the date. */
  static empty(date: string): Transaction {
    return new Transaction(
      new EntryMetadata(),
      date,
      "",
      "*",
      "",
      "",
      [],
      [],
      [],
    );
  }

  /** Combine narration, tags, and links for a single `<input>`. */
  get_narration_tags_links(): string {
    let val = this.narration;
    if (this.tags.length) {
      val += ` ${this.tags.map((t) => `#${t}`).join(" ")}`;
    }
    if (this.links.length) {
      val += ` ${this.links.map((t) => `^${t}`).join(" ")}`;
    }
    return val;
  }

  /** Set narration, tags, and links from a single string. */
  set_narration_tags_links(value: string): Transaction {
    const tags = [...value.matchAll(TAGS_RE)].map((a) => a[1] ?? "");
    const links = [...value.matchAll(LINKS_RE)].map((a) => a[1] ?? "");
    const narration = value
      .replaceAll(TAGS_RE, "")
      .replaceAll(LINKS_RE, "")
      .trim();
    return new Transaction(
      this.meta,
      this.date,
      this.entry_hash,
      this.flag,
      this.payee,
      narration,
      tags,
      links,
      this.postings,
    );
  }

  override toString(): string {
    const postings = this.postings.map((p) => `  ${p.account}  ${p.amount}`);
    return (
      `${this.date} ${this.flag} "${this.payee}" "${this.narration}"` +
      `\n${postings.join("\n")}`
    );
  }

  toJSON(): ValidationT<typeof Transaction.raw_validator> {
    return {
      t: this.t,
      meta: this.meta,
      date: this.date,
      entry_hash: this.entry_hash,
      flag: this.flag,
      payee: this.payee,
      narration: this.narration,
      tags: this.tags,
      links: this.links,
      postings: this.postings.filter((p) => !p.is_empty()),
    };
  }

  private static raw_validator = object({
    t: constant("Transaction"),
    meta: EntryMetadata.validator,
    date: string,
    entry_hash: string,
    flag: string,
    payee: optional_string,
    narration: optional_string,
    tags: string_array_validator,
    links: string_array_validator,
    postings: array(Posting.validator),
  });

  static validator: Validator<Transaction> = (json) =>
    Transaction.raw_validator(json).map(
      ({
        meta,
        date,
        entry_hash,
        flag,
        payee,
        narration,
        tags,
        links,
        postings,
      }) =>
        new Transaction(
          meta,
          date,
          entry_hash,
          flag,
          payee,
          narration,
          tags,
          links,
          postings,
        ),
    );
}

/** Validate an Entry. */
export const entryValidator = tagged_union("t", {
  Balance: Balance.validator,
  Close: Close.validator,
  Custom: Custom.validator,
  Document: Document.validator,
  Event: Event.validator,
  Note: Note.validator,
  Open: Open.validator,
  Pad: Pad.validator,
  Price: Price.validator,
  Query: Query.validator,
  Transaction: Transaction.validator,
});

/** A Beancount entry, currently only supports some of the types. */
export type Entry = ValidationT<typeof entryValidator>;
