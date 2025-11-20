import { object, optional, type Validator } from "../lib/validation.ts";
import { Amount } from "./amount.ts";
import { Cost } from "./cost.ts";

/** A position, a pair of units and cost. */

export class Position {
  readonly units: Amount;
  readonly cost: Cost | null;

  constructor(units: Amount, cost: Cost | null) {
    this.units = units;
    this.cost = cost;
  }

  private static raw_validator = object({
    units: Amount.validator,
    cost: optional(Cost.validator),
  });

  static validator: Validator<Position> = (json) =>
    Position.raw_validator(json).map(
      ({ units, cost }) => new Position(units, cost),
    );
}
