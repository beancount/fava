import { event, select, Selection } from "d3-selection";

import e from "../events";

export const tooltip = select(document.body)
  .append("div")
  .attr("class", "tooltip");

// Add a tooltip to the given selection.
export function addTooltip<S extends Element, T>(
  selection: Selection<S, T, Element, unknown>,
  tooltipText: (d: T) => string
) {
  selection
    .on("mouseenter", (d: T) => {
      tooltip.style("opacity", 1).html(tooltipText(d));
    })
    .on("mousemove", () => {
      tooltip
        .style("left", `${event.pageX}px`)
        .style("top", `${event.pageY - 15}px`);
    })
    .on("mouseleave", () => {
      tooltip.style("opacity", 0);
    });
}

e.on("page-loaded", () => {
  tooltip.style("opacity", 0);
});
