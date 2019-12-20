import {
  partition,
  PartitionLayout,
  treemap,
  TreemapLayout,
  HierarchyNode,
  HierarchyRectangularNode,
} from "d3-hierarchy";
import { scaleLinear, scaleSqrt, ScaleLinear, ScalePower } from "d3-scale";
import { event, select, Selection } from "d3-selection";
import { arc, Arc } from "d3-shape";
import "d3-transition";

import { favaAPI } from "../stores";
import { formatCurrency, formatPercentage } from "../format";

import { BaseChart } from "./base";
import { NO_MARGINS, scales } from "./helpers";
import { addTooltip } from "./tooltip";

interface AccountHierarchyDatum {
  account: string;
  balance: Record<string, number>;
  dummy?: boolean;
}
export interface AccountHierarchy extends AccountHierarchyDatum {
  children: AccountHierarchy[];
}
export type AccountHierarchyNode = HierarchyNode<AccountHierarchyDatum>;

/**
 * Add internal nodes as fake leaf nodes to their own children.
 *
 * In the treemap, we only render leaf nodes, so for accounts that have both
 * children and a balance, we want to duplicate them as leaf nodes.
 */
export function addInternalNodesAsLeaves(node: AccountHierarchy) {
  if (node.children.length) {
    node.children.forEach(addInternalNodesAsLeaves);
    node.children.push({ ...node, children: [], dummy: true });
    node.balance = {};
  }
}

// Turn the elements in the selection (assuming they have a .account attribute)
// into links to the account page.
function makeAccountLink(
  selection:
    | Selection<SVGTextElement, TreemapDatum, Element, unknown>
    | Selection<SVGPathElement, TreemapDatum, Element, unknown>
    | Selection<SVGTextElement, TreemapDatum, null, undefined>
) {
  selection.on("click", d => {
    window.location.href = favaAPI.accountURL.replace(
      "REPLACEME",
      d.data.account
    );
    event.stopPropagation();
  });
}

type TreemapDatum = HierarchyRectangularNode<AccountHierarchyDatum>;

class TreeMapChart extends BaseChart {
  treemap: TreemapLayout<any>;

  root?: TreemapDatum;

  canvas: Selection<SVGElement, unknown, null, undefined>;

  cells: Selection<SVGGElement, TreemapDatum, Element, unknown>;

  labels: Selection<SVGTextElement, TreemapDatum, Element, unknown>;

  tooltipText?: (d: TreemapDatum) => string;

  constructor(svg: SVGElement) {
    super(svg);
    this.treemap = treemap().paddingInner(2);
    this.margin = NO_MARGINS;

    this.canvas = select(svg).classed("treemap", true);
    this.cells = this.canvas.selectAll("g");
    this.labels = this.cells.append("text");
  }

  draw(data: AccountHierarchyNode) {
    this.root = this.treemap(data);

    this.cells = this.canvas
      .selectAll("g")
      .data(this.root.leaves())
      .enter()
      .append("g")
      .call(addTooltip, this.tooltipText);

    this.cells.append("rect").attr("fill", d => {
      const node = d.data.dummy ? d.parent! : d;
      if (node.parent === this.root || !node.parent) {
        return scales.treemap(node.data.account);
      }
      return scales.treemap(node.parent.data.account);
    });

    this.labels = this.cells
      .append("text")
      .attr("dy", ".5em")
      .attr("text-anchor", "middle")
      .text(d => d.data.account.split(":").pop() || "")
      .style("opacity", 0)
      .call(makeAccountLink);

    this.update();
    return this;
  }

  update() {
    this.setHeight(Math.min(this.width / 2.5, 400));

    if (!this.root) {
      return;
    }

    this.treemap.size([this.width, this.height]);
    this.treemap(this.root);

    function labelOpacity(this: SVGTextElement, d: TreemapDatum) {
      const length = this.getComputedTextLength();
      return d.x1 - d.x0 > length + 4 && d.y1 - d.y0 > 14 ? 1 : 0;
    }

    this.cells.attr("transform", d => `translate(${d.x0},${d.y0})`);

    this.cells
      .select("rect")
      .attr("width", d => d.x1 - d.x0)
      .attr("height", d => d.y1 - d.y0);

    this.labels
      .attr("x", d => (d.x1 - d.x0) / 2)
      .attr("y", d => (d.y1 - d.y0) / 2)
      .style("opacity", labelOpacity);
  }
}

class SunburstChart extends BaseChart {
  canvas: Selection<SVGGElement, unknown, null, undefined>;

  root?: TreemapDatum;

  arc: Arc<any, TreemapDatum>;

  x: ScaleLinear<number, number>;

  y: ScalePower<number, number>;

  partition: PartitionLayout<AccountHierarchyDatum>;

  labelText?: (d: TreemapDatum) => string;

  accountLabel: Selection<SVGTextElement, unknown, null, undefined>;

  balanceLabel: Selection<SVGTextElement, unknown, null, undefined>;

  paths: Selection<SVGPathElement, TreemapDatum, Element, unknown>;

  boundingCircle: Selection<SVGCircleElement, unknown, null, undefined>;

  constructor(svg: SVGElement) {
    super(svg);
    this.margin = NO_MARGINS;

    this.x = scaleLinear().range([0, 2 * Math.PI]);
    this.y = scaleSqrt();
    this.partition = partition();
    this.arc = arc<TreemapDatum>()
      .startAngle(d => this.x(d.x0))
      .endAngle(d => this.x(d.x1))
      .innerRadius(d => this.y(d.y0))
      .outerRadius(d => this.y(d.y1));

    this.canvas = select(this.svg)
      .attr("class", "sunburst")
      .append("g")
      .on("mouseleave", () => this.mouseLeave());

    // Bounding circle underneath the sunburst
    this.boundingCircle = this.canvas.append("circle").style("opacity", 0);

    this.accountLabel = this.canvas
      .append("text")
      .attr("class", "account")
      .attr("text-anchor", "middle");

    this.balanceLabel = this.canvas
      .append("text")
      .attr("class", "balance")
      .attr("dy", "1.2em")
      .attr("text-anchor", "middle");

    this.paths = this.canvas.selectAll("path");
  }

  draw(data: AccountHierarchyNode) {
    this.root = this.partition(data);

    this.paths = this.canvas
      .selectAll("path")
      .data(this.root.descendants())
      .enter()
      .filter(d => !d.data.dummy && !!d.depth)
      .append("path")
      .attr("fill-rule", "evenodd")
      .style("fill", d => scales.sunburst(d.data.account))
      .on("mouseover", d => this.mouseOver(d))
      .call(makeAccountLink);

    this.update();
    this.setLabel(this.root);
    return this;
  }

  update() {
    this.canvas.attr(
      "transform",
      `translate(${this.width / 2 + this.margin.left},${this.height / 2 +
        this.margin.top})`
    );

    const radius = Math.min(this.width, this.height) / 2;
    this.boundingCircle.attr("r", radius);
    this.y.range([0, radius]);
    this.paths.attr("d", this.arc);
  }

  setLabel(d: TreemapDatum) {
    if (this.labelText) {
      this.balanceLabel.text(this.labelText(d));
    }
    this.accountLabel
      .datum(d)
      .text(d.data.account)
      .call(makeAccountLink);
  }

  // Fade all but the current sequence
  mouseOver(d: TreemapDatum) {
    this.setLabel(d);
    this.paths.interrupt();

    // Only highlight segments that are ancestors of the current segment.
    this.paths
      .style("opacity", 0.5)
      // check if d.account starts with node.account
      .filter(node => d.data.account.lastIndexOf(node.data.account, 0) === 0)
      .style("opacity", 1);
  }

  // Restore everything to full opacity when moving off the visualization.
  mouseLeave() {
    this.paths
      .transition()
      .duration(1000)
      .style("opacity", 1);
    if (this.root) {
      this.setLabel(this.root);
    }
  }
}

class SunburstChartContainer extends BaseChart {
  currencies: string[];

  canvases: Selection<SVGGElement, unknown, null, undefined>[];

  sunbursts: SunburstChart[];

  constructor(svg: SVGElement) {
    super(svg);

    this.svg.setAttribute("class", "sunburst");
    this.sunbursts = [];
    this.canvases = [];
    this.margin = NO_MARGINS;
    this.currencies = [];

    this.setHeight(500);
  }

  draw(data: Record<string, AccountHierarchyNode>) {
    this.currencies = Object.keys(data);

    this.currencies.forEach((currency, i) => {
      const canvas = select(this.svg)
        .append("g")
        .attr(
          "transform",
          `translate(${(this.width * i) / this.currencies.length},0)`
        );

      const totalBalance = data[currency].value || 1;
      const sunburst = new SunburstChart(canvas.node()!)
        .setWidth(this.width / this.currencies.length)
        .setHeight(500)
        .set("labelText", d => {
          const balance = d.value || 0;
          return `${formatCurrency(balance)} ${currency} (${formatPercentage(
            balance / totalBalance
          )})`;
        })
        .draw(data[currency]);

      this.canvases.push(canvas);
      this.sunbursts.push(sunburst);
    });

    return this;
  }

  update() {
    this.sunbursts.forEach((singleChart, i) => {
      singleChart
        .setWidth(this.width / this.currencies.length)
        .setHeight(500)
        .update();
      this.canvases[i].attr(
        "transform",
        `translate(${(this.width * i) / this.currencies.length},0)`
      );
    });
  }
}

export class HierarchyContainer extends BaseChart {
  canvas: SVGGElement;

  data?: Record<string, AccountHierarchyNode>;

  currency: string;

  currencies: string[];

  currentChart?: TreeMapChart | SunburstChartContainer;

  mode: "treemap" | "sunburst";

  constructor(svg: SVGElement) {
    super(svg);
    this.canvas = document.createElementNS("http://www.w3.org/2000/svg", "g");
    svg.appendChild(this.canvas);
    this.has_mode_setting = true;
    this.margin = NO_MARGINS;
    this.currencies = [];
    this.currency = "";
    this.mode = "treemap";
  }

  draw(data: Record<string, AccountHierarchyNode>) {
    this.data = data;
    this.currencies = Object.keys(data);

    this.canvas.innerHTML = "";

    if (this.currencies.length === 0) {
      select(this.canvas)
        .append("text")
        .text("Chart is empty.")
        .attr("text-anchor", "middle")
        .attr("x", this.width / 2)
        .attr("y", 160 / 2);
    } else if (this.mode === "treemap") {
      if (!this.currency) {
        [this.currency] = this.currencies;
      }
      const totalBalance = data[this.currency].value || 1;
      const currentChart = new TreeMapChart(this.canvas)
        .setWidth(this.width)
        .set("tooltipText", d => {
          const balance = d.data.balance[this.currency];
          return `${formatCurrency(balance)} ${
            this.currency
          } (${formatPercentage(balance / totalBalance)})<em>${
            d.data.account
          }</em>`;
        })
        .draw(data[this.currency]);

      this.setHeight(currentChart.outerHeight);
      this.currentChart = currentChart;
      this.has_currency_setting = true;
    } else {
      this.currentChart = new SunburstChartContainer(this.canvas)
        .setWidth(this.width)
        .draw(data);

      this.setHeight(this.currentChart.outerHeight);
      this.has_currency_setting = false;
    }

    return this;
  }

  update() {
    if (!this.data) {
      return;
    }
    this.draw(this.data);
    if (this.currentChart) {
      this.currentChart.setWidth(this.outerWidth).update();
    }
  }
}
