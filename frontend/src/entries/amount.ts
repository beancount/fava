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
