import { object, optional, type Validator } from "../lib/validation";
import { Amount } from "./amount";
import { Cost } from "./cost";

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
