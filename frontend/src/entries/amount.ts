import type { FormatterContext } from "../format";
import type { Validator } from "../lib/validation";
import { number, object, string } from "../lib/validation";

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

/** A raw amount is a pair of number (as a string) and currency. */
export class RawAmount {
  constructor(
    readonly number: string,
    readonly currency: string,
  ) {}

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
