import { is_empty } from "../lib/objects";
import { ok } from "../lib/result";
import type { SafeValidator, Validator } from "../lib/validation";
import { record } from "../lib/validation";

export type MetadataValue = string | boolean | number;

const entry_meta_item: SafeValidator<MetadataValue> = (json) => {
  if (
    typeof json === "boolean" ||
    typeof json === "number" ||
    typeof json === "string"
  ) {
    return ok(json);
  }
  return ok("Unsupported metadata value");
};

/**
 * Convert a metadata value to a string ready for an input field.
 * @param value - the metadata value.
 */
function meta_value_to_string(value: MetadataValue): string {
  if (typeof value === "boolean") {
    return value ? "TRUE" : "FALSE";
  }
  return typeof value === "string" ? value : value.toString();
}

/**
 * Convert a string to a metadata value.
 * @param s - The string that the user entered.
 */
function string_to_meta_value(s: string): MetadataValue {
  if (s === "TRUE") {
    return true;
  }
  if (s === "FALSE") {
    return false;
  }
  return s;
}

/** Metadate of a entry or posting. */
export class EntryMetadata {
  #meta: Readonly<Record<string, MetadataValue>>;

  constructor(meta?: Record<string, MetadataValue>) {
    this.#meta = meta ?? {};
  }

  /** Whether the metadata is empty. */
  is_empty(): boolean {
    return is_empty(this.#meta);
  }

  /** Get the filename, falling back to an empty string if missing. */
  get filename(): string {
    return this.#meta.filename?.toString() ?? "";
  }

  /** Get the line number as a string, falling back to an empty string if missing. */
  get lineno(): string {
    return this.#meta.lineno?.toString() ?? "";
  }

  toJSON(): Record<string, MetadataValue> {
    return this.#meta;
  }

  /** Delete a key from the metadata and return an updated copy. */
  delete(key: string): EntryMetadata {
    const { [key]: _ignored, ...rest } = this.#meta;
    return new EntryMetadata(rest);
  }

  /** All metadata entries (values as strings), filtering out hidden ones. */
  entries(): [key: string, value: string][] {
    return Object.entries(this.#meta)
      .filter(
        ([key]) =>
          !key.startsWith("_") && key !== "filename" && key !== "lineno",
      )
      .map(([key, value]) => [key, meta_value_to_string(value)]);
  }

  /** Get the value for a key. */
  get(key: string): MetadataValue | undefined {
    return this.#meta[key];
  }

  /** Set the value for a key and return an updated copy. */
  set(key: string, value: MetadataValue): EntryMetadata {
    return new EntryMetadata({ ...this.#meta, [key]: value });
  }

  /** Set the value for a key from a string and return an updated copy. */
  set_string(key: string, value: string): EntryMetadata {
    return this.set(key, string_to_meta_value(value));
  }

  /** Add a new empty key and value and return an updated copy. */
  add(): EntryMetadata {
    return this.set("", "");
  }

  /** Change a key and a return an updated copy. */
  update_key(current_key: string, new_key: string): EntryMetadata {
    return new EntryMetadata(
      Object.fromEntries(
        Object.entries(this.#meta).map(([key, value]) => [
          key === current_key ? new_key : key,
          value,
        ]),
      ),
    );
  }

  private static raw_validator = record(entry_meta_item);

  static validator: Validator<EntryMetadata> = (json) =>
    EntryMetadata.raw_validator(json).map((meta) => new EntryMetadata(meta));
}
