import type { ValidationT, Validator } from "../lib/validation";
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
}

export const entryBaseValidator = object<EntryBaseAttributes>({
  t: string,
  meta: EntryMetadata.validator,
  date: string,
});

abstract class EntryBase<T extends string> {
  constructor(
    readonly t: T,
    readonly meta: EntryMetadata,
    readonly date: string,
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

interface RawAmount {
  readonly number: string;
  readonly currency: string;
}

/** A balance. */
export class Balance extends EntryBase<"Balance"> {
  private constructor(
    meta: EntryMetadata,
    date: string,
    readonly account: string,
    readonly amount: RawAmount,
  ) {
    super("Balance", meta, date);
  }

  /** Create a new empty Balance entry on the date. */
  static empty(date: string): Balance {
    return new Balance(new EntryMetadata(), date, "", {
      number: "",
      currency: "",
    });
  }

  private static raw_validator = object({
    t: constant("Balance"),
    meta: EntryMetadata.validator,
    date: string,
    account: string,
    amount: object({ number: string, currency: string }),
  });

  static validator: Validator<Balance> = (json) =>
    Balance.raw_validator(json).map(
      ({ date, meta, account, amount }) =>
        new Balance(meta, date, account, amount),
    );
}

/** A document. */
export class Document extends EntryBase<"Document"> {
  private constructor(
    meta: EntryMetadata,
    date: string,
    readonly account: string,
    readonly filename: string,
  ) {
    super("Document", meta, date);
  }

  private static raw_validator = object({
    t: constant("Document"),
    meta: EntryMetadata.validator,
    date: string,
    account: string,
    filename: string,
  });

  static validator: Validator<Document> = (json) =>
    Document.raw_validator(json).map(
      ({ date, meta, account, filename }) =>
        new Document(meta, date, account, filename),
    );
}

/** An event. */
export class Event extends EntryBase<"Event"> {
  private constructor(
    meta: EntryMetadata,
    date: string,
    readonly type: string,
    readonly description: string,
  ) {
    super("Event", meta, date);
  }

  private static raw_validator = object({
    t: constant("Event"),
    meta: EntryMetadata.validator,
    date: string,
    type: string,
    description: string,
  });

  static validator: Validator<Event> = (json) =>
    Event.raw_validator(json).map(
      ({ meta, date, type, description }) =>
        new Event(meta, date, type, description),
    );
}

/** A note. */
export class Note extends EntryBase<"Note"> {
  private constructor(
    meta: EntryMetadata,
    date: string,
    readonly account: string,
    readonly comment: string,
  ) {
    super("Note", meta, date);
  }

  /** Create a new empty Note entry on the date. */
  static empty(date: string): Note {
    return new Note(new EntryMetadata(), date, "", "");
  }

  private static raw_validator = object({
    t: constant("Note"),
    meta: EntryMetadata.validator,
    date: string,
    account: string,
    comment: string,
  });

  static validator: Validator<Note> = (json) =>
    Note.raw_validator(json).map(
      ({ meta, date, account, comment }) =>
        new Note(meta, date, account, comment),
    );
}

const TAGS_RE = /(?:^|\s)#([A-Za-z0-9\-_/.]+)/g;
const LINKS_RE = /(?:^|\s)\^([A-Za-z0-9\-_/.]+)/g;

/** A transaction. */
export class Transaction extends EntryBase<"Transaction"> {
  private constructor(
    meta: EntryMetadata,
    date: string,
    readonly flag: string,
    readonly payee: string,
    readonly narration: string,
    readonly tags: string[],
    readonly links: string[],
    readonly postings: readonly Posting[],
  ) {
    super("Transaction", meta, date);
  }

  /** Create a new empty Transaction entry on the date. */
  static empty(date: string): Transaction {
    return new Transaction(new EntryMetadata(), date, "*", "", "", [], [], []);
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
    flag: string,
    payee: optional_string,
    narration: optional_string,
    tags: array(string),
    links: array(string),
    postings: array(Posting.validator),
  });

  static validator: Validator<Transaction> = (json) =>
    Transaction.raw_validator(json).map(
      ({ meta, date, flag, payee, narration, tags, links, postings }) =>
        new Transaction(
          meta,
          date,
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
  Document: Document.validator,
  Event: Event.validator,
  Note: Note.validator,
  Transaction: Transaction.validator,
});

/** A Beancount entry, currently only supports some of the types. */
export type Entry = ValidationT<typeof entryValidator>;
