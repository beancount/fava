import type { FormatterContext } from "../format.ts";
import type { Validator } from "../lib/validation.ts";
import { number, object, string } from "../lib/validation.ts";

/** An amount is a pair of number and currency. */
export class Amount {
  readonly number: number;
  readonly currency: string;

  constructor(number: number, currency: string) {
    this.number = number;
    this.currency = currency;
  }

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

/** A raw amount is a pair of number (as a string) and currency. */
export class RawAmount {
  readonly number: string;
  readonly currency: string;

  constructor(number: string, currency: string) {
    this.number = number;
    this.currency = currency;
  }

  /** Set the currency return an updated copy. */
  set_currency(currency: string): RawAmount {
    return new RawAmount(this.number, currency);
  }

  /** Set the number and return an updated copy. */
  set_number(number: string): RawAmount {
    return new RawAmount(number, this.currency);
  }

  static empty(): RawAmount {
    return new RawAmount("", "");
  }

  private static raw_validator = object({ number: string, currency: string });

  static validator: Validator<RawAmount> = (json) =>
    RawAmount.raw_validator(json).map(
      ({ number, currency }) => new RawAmount(number, currency),
    );
}
