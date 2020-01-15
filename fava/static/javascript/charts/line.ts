import { max, merge, min } from "d3-array";
import { axisLeft, axisBottom, Axis } from "d3-axis";
import { scaleLinear, scaleUtc, ScaleLinear, ScaleTime } from "d3-scale";
import { event, clientPoint, select, Selection, BaseType } from "d3-selection";
import { line, Line } from "d3-shape";
import { quadtree, Quadtree } from "d3-quadtree";

import { formatCurrencyShort } from "../format";

import { BaseChart } from "./base";
import { scales } from "./helpers";
import { tooltip } from "./tooltip";

export interface LineChartDatum {
  name: string;
  date: Date;
  value: number;
}

export type LineChartData = {
  name: string;
  values: LineChartDatum[];
};

export class LineChart extends BaseChart {
  canvas: Selection<SVGGElement, unknown, null, undefined>;

  data: LineChartData[];

  x: ScaleTime<number, number>;

  y: ScaleLinear<number, number>;

  xAxis: Axis<Date>;

  xAxisSelection: Selection<SVGGElement, unknown, null, undefined>;

  yAxis: Axis<number>;

  yAxisSelection: Selection<SVGGElement, unknown, null, undefined>;

  line: Line<LineChartDatum>;

  tooltipText?: (d: LineChartDatum) => string;

  quadtree: Quadtree<LineChartDatum>;

  lines: Selection<SVGPathElement, LineChartData, SVGGElement, unknown>;

  dots: Selection<SVGCircleElement, LineChartDatum, BaseType, unknown>;

  constructor(svg: SVGElement) {
    super(svg);

    this.data = [];
    this.x = scaleUtc();
    this.y = scaleLinear();

    this.xAxis = axisBottom<Date>(this.x).tickSizeOuter(0);

    this.yAxis = axisLeft<number>(this.y)
      .tickPadding(6)
      .tickFormat(formatCurrencyShort);

    this.line = line<LineChartDatum>()
      .x(d => this.x(d.date))
      .y(d => this.y(d.value));

    this.canvas = select(this.svg)
      .classed("linechart", true)
      .append("g");
    this.xAxisSelection = this.canvas.append("g").attr("class", "x axis");
    this.yAxisSelection = this.canvas.append("g").attr("class", "y axis");
    this.quadtree = quadtree();
    this.lines = this.canvas.selectAll(".line");
    this.dots = this.canvas.selectAll("g.dot").selectAll("circle");
  }

  draw(data: LineChartData[]) {
    this.data = data;
    this.x.domain([
      min(this.data, s => s.values[0].date) || 0,
      max(this.data, s => s.values[s.values.length - 1].date) || 0,
    ]);

    // Span y-axis as max minus min value plus 5 percent margin
    const minDataValue = min(this.data, d => min(d.values, x => x.value));
    const maxDataValue = max(this.data, d => max(d.values, x => x.value));
    if (minDataValue !== undefined && maxDataValue !== undefined) {
      this.y.domain([
        minDataValue - (maxDataValue - minDataValue) * 0.05,
        maxDataValue + (maxDataValue - minDataValue) * 0.05,
      ]);
    }

    this.lines = this.canvas
      .selectAll(".line")
      .data(data)
      .enter()
      .append("path")
      .attr("class", "line")
      .style("stroke", d => scales.currencies(d.name));

    this.dots = this.canvas
      .selectAll("g.dot")
      .data(data)
      .enter()
      .append("g")
      .attr("class", "dot")
      .style("fill", d => scales.currencies(d.name))
      .selectAll("circle")
      .data(d => d.values)
      .enter()
      .append("circle")
      .attr("r", 3);

    const canvasNode = this.canvas.node()!;
    this.canvas
      .on("mousemove", () => {
        const matrix = canvasNode.getScreenCTM();
        const d = this.quadtree.find(...clientPoint(canvasNode, event));
        if (this.tooltipText && matrix && d) {
          tooltip
            .style("opacity", 1)
            .html(this.tooltipText(d))
            .style("left", `${window.scrollX + this.x(d.date) + matrix.e}px`)
            .style(
              "top",
              `${window.scrollY + this.y(d.value) + matrix.f - 15}px`
            );
        } else {
          tooltip.style("opacity", 0);
        }
      })
      .on("mouseleave", () => {
        tooltip.style("opacity", 0);
      });

    this.update();
    return this;
  }

  update() {
    this.setHeight(250);

    this.y.range([this.height, 0]);
    this.x.range([0, this.width]);

    this.canvas.attr(
      "transform",
      `translate(${this.margin.left},${this.margin.top})`
    );

    this.yAxis.tickSize(-this.width);
    this.xAxisSelection.attr("transform", `translate(0,${this.height})`);

    this.xAxisSelection.call(this.xAxis);
    this.yAxisSelection.call(this.yAxis);
    this.dots.attr("cx", d => this.x(d.date)).attr("cy", d => this.y(d.value));
    this.lines.attr("d", d => this.line(d.values));

    this.quadtree = quadtree(
      merge(this.data.map(d => d.values)),
      d => this.x(d.date),
      d => this.y(d.value)
    );

    this.legend = {
      domain: this.data.map(d => d.name),
      scale: scales.currencies,
    };
  }
}
