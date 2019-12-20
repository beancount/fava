import { extent } from "d3-array";
import { axisLeft, axisBottom, Axis } from "d3-axis";
import { scalePoint, scaleUtc, ScaleTime, ScalePoint } from "d3-scale";
import { event, clientPoint, select, Selection } from "d3-selection";
import { quadtree, Quadtree } from "d3-quadtree";
import "d3-transition";

import { BaseChart } from "./base";
import { scales } from "./helpers";
import { dateFormat } from "../format";
import { tooltip } from "./tooltip";

export interface ScatterPlotDatum {
  date: Date;
  type: string;
  description: string;
}

export class ScatterPlot extends BaseChart {
  canvas: Selection<SVGGElement, unknown, null, undefined>;

  data: ScatterPlotDatum[];

  x: ScaleTime<number, number>;

  y: ScalePoint<string>;

  xAxis: Axis<Date>;

  xAxisSelection: Selection<SVGGElement, unknown, null, undefined>;

  yAxis: Axis<string>;

  yAxisSelection: Selection<SVGGElement, unknown, null, undefined>;

  dots: Selection<SVGCircleElement, ScatterPlotDatum, Element, unknown>;

  quadtree: Quadtree<ScatterPlotDatum>;

  constructor(svg: SVGElement) {
    super(svg);
    this.canvas = select(this.svg)
      .classed("scatterplot", true)
      .append("g");
    this.margin.left = 70;

    this.x = scaleUtc();
    this.y = scalePoint().padding(1);

    this.xAxis = axisBottom<Date>(this.x).tickSizeOuter(0);

    this.yAxis = axisLeft(this.y)
      .tickPadding(6)
      .tickFormat(d => d);
    this.data = [];
    this.quadtree = quadtree<ScatterPlotDatum>();

    this.xAxisSelection = this.canvas.append("g").attr("class", "x axis");
    this.yAxisSelection = this.canvas.append("g").attr("class", "y axis");
    this.dots = this.canvas.selectAll(".dot");
  }

  draw(data: ScatterPlotDatum[]) {
    this.data = data;
    const dateExtent = extent(data, d => d.date);
    if (dateExtent[0] !== undefined) {
      this.x.domain(dateExtent);
    }
    this.y.domain(data.map(d => d.type));

    this.dots = this.canvas
      .selectAll(".dot")
      .data(this.data)
      .enter()
      .append("circle")
      .attr("class", "dot")
      .attr("r", 5)
      .style("fill", d => scales.scatterplot(d.type));

    const canvasNode = this.canvas.node()!;
    this.canvas
      .on("mousemove", () => {
        const matrix = canvasNode.getScreenCTM();
        if (!matrix) {
          return;
        }
        const d = this.quadtree.find(...clientPoint(canvasNode, event));
        if (d) {
          tooltip
            .style("opacity", 1)
            .html(this.tooltipText(d))
            .style("left", `${window.scrollX + this.x(d.date) + matrix.e}px`)
            .style(
              "top",
              `${window.scrollY + this.y(d.type)! + matrix.f - 15}px`
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

  // eslint-disable-next-line class-methods-use-this
  tooltipText(d: ScatterPlotDatum) {
    return `${d.description}<em>${dateFormat.day(d.date)}</em>`;
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
    this.dots.attr("cx", d => this.x(d.date)).attr("cy", d => this.y(d.type)!);

    this.quadtree = quadtree<ScatterPlotDatum>(
      this.data,
      d => this.x(d.date),
      d => this.y(d.type)!
    );
  }
}
