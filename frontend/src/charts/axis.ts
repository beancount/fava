import { Axis } from "d3-axis";
import { select } from "d3-selection";

export function axis<T>(
  node: SVGGElement,
  ax: Axis<T>
): { update: (a: Axis<T>) => void } {
  const selection = select(node);
  ax(selection);

  return {
    update(a: Axis<T>): void {
      a(selection);
    },
  };
}
