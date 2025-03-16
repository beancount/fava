import { day as format_day, type FormatterContext } from "../format";
import {
  date,
  number,
  object,
  optional,
  optional_string,
  string,
  type Validator,
} from "../lib/validation";

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
      strs.push(format_day(this.date));
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
