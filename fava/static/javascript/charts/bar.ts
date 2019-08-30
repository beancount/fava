import { max, min } from "d3-array";
import { axisLeft, axisBottom, Axis } from "d3-axis";
import { scaleBand, scaleLinear, ScaleLinear, ScaleBand } from "d3-scale";
import { select, Selection } from "d3-selection";

import { formatCurrencyShort } from "../format";

import { BaseChart } from "./base";
import { scales, setTimeFilter } from "./helpers";
import { addTooltip } from "./tooltip";

const maxColumnWidth = 100;

interface BarChartDatumValue {
  name: string;
  value: number;
  budget: number;
}

interface BarChartDatum {
  label: string;
  date: Date;
  values: BarChartDatumValue[];
}

export class BarChart extends BaseChart {
  canvas: Selection<SVGGElement, unknown, null, undefined>;

  x0: ScaleBand<string>;

  x1: ScaleBand<string>;

  y: ScaleLinear<number, number>;

  xAxis: Axis<string>;

  xAxisSelection: Selection<SVGGElement, unknown, null, undefined>;

  yAxis: Axis<number>;

  yAxisSelection: Selection<SVGGElement, unknown, null, undefined>;

  groups: Selection<SVGGElement, BarChartDatum, Element, unknown>;

  groupboxes: Selection<SVGRectElement, BarChartDatum, Element, unknown>;

  axisgroupboxes: Selection<SVGRectElement, BarChartDatum, Element, unknown>;

  bars: Selection<SVGRectElement, BarChartDatumValue, Element, unknown>;

  budgets: Selection<SVGRectElement, BarChartDatumValue, Element, unknown>;

  tooltipText?: (d: BarChartDatum) => string;

  constructor(svg: SVGElement) {
    super(svg);

    this.x0 = scaleBand().padding(0.1);
    this.x1 = scaleBand();
    this.y = scaleLinear();

    this.xAxis = axisBottom(this.x0).tickSizeOuter(0);
    this.yAxis = axisLeft<number>(this.y).tickFormat(formatCurrencyShort);

    this.svg.setAttribute("class", "barchart");
    this.canvas = select(this.svg)
      .classed("barchart", true)
      .append("g");
    this.xAxisSelection = this.canvas.append("g").attr("class", "x axis");
    this.yAxisSelection = this.canvas.append("g").attr("class", "y axis");

    this.groups = this.canvas.selectAll(".group");
    this.groupboxes = this.groups.append("rect");
    this.axisgroupboxes = this.groups.append("rect");
    this.bars = this.groups.selectAll(".bar");
    this.budgets = this.groups.selectAll(".budget");
  }

  draw(data: BarChartDatum[]) {
    this.x0.domain(data.map(d => d.label));
    this.x1.domain(data[0].values.map(d => d.name));

    this.y.domain([
      Math.min(0, min(data, d => min(d.values, x => x.value)) || 0),
      Math.max(0, max(data, d => max(d.values, x => x.value)) || 0),
    ]);

    this.groups = this.canvas
      .selectAll(".group")
      .data(data)
      .enter()
      .append("g")
      .attr("class", "group")
      .call(addTooltip, this.tooltipText);

    this.groupboxes = this.groups.append("rect").attr("class", "group-box");

    this.axisgroupboxes = this.groups
      .append("rect")
      .on("click", d => {
        setTimeFilter(d.date);
      })
      .attr("class", "axis-group-box");

    this.bars = this.groups
      .selectAll(".bar")
      .data(d => d.values)
      .enter()
      .append("rect")
      .attr("class", "bar")
      .style("fill", d => scales.currencies(d.name));

    this.budgets = this.groups
      .selectAll(".budget")
      .data(d => d.values)
      .enter()
      .append("rect")
      .attr("class", "budget");

    this.update();
    return this;
  }

  update() {
    const screenWidth = this.width;
    const maxWidth = this.groups.size() * maxColumnWidth;
    const offset = this.margin.left + Math.max(0, screenWidth - maxWidth) / 2;

    this.width = Math.min(screenWidth, maxWidth);
    this.setHeight(250);

    this.y.range([this.height, 0]);
    this.x0.range([0, this.width]);
    this.x1.range([0, this.x0.bandwidth()]);

    this.canvas.attr("transform", `translate(${offset},${this.margin.top})`);

    this.yAxis.tickSize(-this.width);
    this.xAxisSelection.attr("transform", `translate(0,${this.height})`);

    this.xAxis.tickValues(this.filterTicks(this.x0.domain()));
    this.xAxisSelection.call(this.xAxis);
    this.yAxisSelection.call(this.yAxis);

    this.groups.attr("transform", d => `translate(${this.x0(d.label)},0)`);

    this.groupboxes
      .attr("width", this.x0.bandwidth())
      .attr("height", this.height);

    this.axisgroupboxes
      .attr("width", this.x0.bandwidth())
      .attr("height", this.margin.bottom)
      .attr("transform", `translate(0,${this.height})`);

    this.budgets
      .attr("width", this.x1.bandwidth())
      .attr("x", d => this.x1(d.name) || 0)
      .attr("y", d => this.y(Math.max(0, d.budget)))
      .attr("height", d => Math.abs(this.y(d.budget) - this.y(0)));

    this.bars
      .attr("width", this.x1.bandwidth())
      .attr("x", d => this.x1(d.name) || 0)
      .attr("y", d => this.y(Math.max(0, d.value)))
      .attr("height", d => Math.abs(this.y(d.value) - this.y(0)));

    this.legend = {
      domain: this.x1.domain(),
      scale: scales.currencies,
    };
  }

  filterTicks(domain: string[]) {
    const labelsCount = this.width / 70;
    if (domain.length <= labelsCount) {
      return domain;
    }
    const showIndices = Math.ceil(domain.length / labelsCount);
    return domain.filter((d, i) => i % showIndices === 0);
  }
}
