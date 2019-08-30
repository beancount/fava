import { ScaleOrdinal } from "d3-scale";

/* The base class for all charts.
 *
 * Provides the following methods:
 *
 * - setHeight(num): set the height of the chart, accounting for margins.
 * - setWidth(num): set the width of the chart, accounting for margins.
 * - set(property, value): set the given property of the chart class to value.
 *
 * Charts should implement the following methods:
 *
 *  - constructor(svg): Initialise the chart, prepare for drawing it to the
 *    given <svg> (which is a d3-selection).
 *  - draw(data): Draw the chart for the given data.
 *  - update(): Update the chart (after resize, toggling, etc)
 */
export abstract class BaseChart {
  svg: SVGElement;

  margin: { top: number; right: number; left: number; bottom: number };

  height: number;

  outerHeight: number;

  width: number;

  outerWidth: number;

  legend?: {
    domain: string[];
    scale: ScaleOrdinal<string, string>;
  };

  has_currency_setting?: boolean;

  has_mode_setting?: boolean;

  constructor(svg: SVGElement) {
    svg.setAttribute("class", "");
    svg.innerHTML = "";
    this.svg = svg;
    this.margin = {
      top: 10,
      right: 10,
      bottom: 30,
      left: 40,
    };
    this.outerHeight = 300;
    this.height = this.outerHeight - this.margin.top - this.margin.bottom;
    this.outerWidth = 500;
    this.width = this.outerWidth - this.margin.left - this.margin.right;
  }

  abstract draw(data: unknown): this;

  setHeight(d: number) {
    this.svg.setAttribute("height", `${d}`);
    this.outerHeight = d;
    this.height = d - this.margin.top - this.margin.bottom;
    return this;
  }

  setWidth(d: number) {
    this.svg.setAttribute("width", `${d}`);
    this.outerWidth = d;
    this.width = d - this.margin.left - this.margin.right;
    return this;
  }

  set<T extends keyof this>(property: T, value: this[T]) {
    this[property] = value;
    return this;
  }
}
