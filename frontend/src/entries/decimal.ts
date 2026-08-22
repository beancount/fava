import type { Validator } from "../lib/validation.ts";
import { object, string } from "../lib/validation.ts";

/** A decimal number, kept as a string to avoid floating point precision loss. */
export class Decimal {
  readonly t: "Decimal";
  readonly value: string;

  constructor(value: string) {
    this.t = "Decimal";
    this.value = value;
  }

  toString(): string {
    return this.value;
  }

  private static raw_validator = object({ value: string });

  static validator: Validator<Decimal> = (json) =>
    Decimal.raw_validator(json).map(({ value }) => new Decimal(value));
}
