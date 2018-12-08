// This module contains the main code to render Fava's charts.
//
// The charts heavily use d3 libraries.

import { extent, max, merge, min } from 'd3-array';
import { axisLeft, axisBottom } from 'd3-axis';
import { hierarchy, partition, treemap } from 'd3-hierarchy';
import {
  scaleBand,
  scaleLinear,
  scaleOrdinal,
  scalePoint,
  scaleSqrt,
  scaleUtc,
} from 'd3-scale';
import { event, select } from 'd3-selection';
import { arc, line } from 'd3-shape';
import { schemeSet3, schemeCategory10 } from 'd3-scale-chromatic';
import { Delaunay } from 'd3-delaunay';
import 'd3-transition';

import e from './events';
import { formatCurrency, formatCurrencyShort, dateFormat } from './format';
import setTimeFilter from './filters';
import { $, $$ } from './helpers';
import router from './router';

// The color scales for the charts.
//
// The scales for treemap and sunburst charts will be initialised with all
// accounts on page init and currencies with all commodities.
const scales = {
  treemap: scaleOrdinal(schemeSet3),
  sunburst: scaleOrdinal(schemeCategory10),
  currencies: scaleOrdinal(schemeCategory10),
  scatterplot: scaleOrdinal(schemeCategory10),
};

let container;
let tooltip;

function addInternalNodesAsLeaves(node) {
  node.children.forEach(o => {
    addInternalNodesAsLeaves(o);
  });
  if (node.children && node.children.length) {
    const copy = $.extend(node);
    copy.children = null;
    copy.dummy = true;
    node.children.push(copy);
    node.balance = {}; // eslint-disable-line no-param-reassign
  }
}

// Turn the elements in the selection (assuming they have a .account attribute)
// into links to the account page.
function makeAccountLink(selection) {
  selection.on('click', d => {
    window.location = window.favaAPI.accountURL.replace(
      'REPLACEME',
      d.data.account,
    );
    event.stopPropagation();
  });
}

// Add a tooltip to the given selection.
function addTooltip(selection, tooltipText) {
  selection
    .on('mouseenter', d => {
      tooltip.style('opacity', 1).html(tooltipText(d));
    })
    .on('mousemove', () => {
      tooltip
        .style('left', `${event.pageX}px`)
        .style('top', `${event.pageY - 15}px`);
    })
    .on('mouseleave', () => {
      tooltip.style('opacity', 0);
    });
}

// Set the chart legend to the given domain.
function setLegend(domain, colorScale) {
  domain.sort();
  const legend = select('#chart-legend')
    .selectAll('span.legend')
    .data(domain)
    .enter()
    .append('span')
    .attr('class', 'legend');

  legend
    .append('span')
    .attr('class', 'color')
    .style('background', d => colorScale(d));

  legend
    .append('span')
    .attr('class', 'name')
    .html(d => d);
}

// Obtain the current value of a <select> and update the list of options.
function setSelect(selector, values) {
  const selectElement = $(selector);
  const { value } = selectElement;
  selectElement.innerHTML = '';
  values.forEach(currency => {
    const opt = document.createElement('option');
    opt.value = currency;
    opt.text = currency;
    if (value === currency) {
      opt.selected = true;
    }
    selectElement.add(opt);
  });
  return values.includes(value) ? value : values[0];
}

// The base class for all charts.
//
// Provides the following methods:
//
// - setHeight(num): set the height of the chart, accounting for margins.
// - setWidth(num): set the width of the chart, accounting for margins.
// - set(property, value): set the given property of the chart class to value.
//
// Charts should implement the following methods:
//
//  - constructor(svg): Initialise the chart, prepare for drawing it to the
//    given <svg> (which is a d3-selection).
//  - draw(data): Draw the chart for the given data.
//  - update(): Update the chart (after resize, toggling, etc)
class BaseChart {
  constructor() {
    this.selections = {};
    this.margin = {
      top: 10,
      right: 10,
      bottom: 30,
      left: 40,
    };
  }

  setHeight(d) {
    this.height = d - this.margin.top - this.margin.bottom;
    return this;
  }

  setWidth(d) {
    this.width = d - this.margin.left - this.margin.right;
    return this;
  }

  set(property, value) {
    this[property] = value;
    return this;
  }
}

class TreeMapChart extends BaseChart {
  constructor(svg) {
    super();
    this.svg = svg;
    this.treemap = treemap();

    this.canvas = svg.classed('treemap', true);
  }

  draw(data) {
    this.root = data;
    this.treemap(this.root);

    this.selections.cells = this.svg
      .selectAll('g')
      .data(this.root.leaves())
      .enter()
      .append('g')
      .call(addTooltip, this.tooltipText);

    this.selections.cells.append('rect').attr('fill', d => {
      const node = d.data.dummy ? d.parent : d;
      if (node.parent === this.root || !node.parent) {
        return scales.treemap(node.data.account);
      }
      return scales.treemap(node.parent.data.account);
    });

    this.selections.cells
      .append('text')
      .attr('dy', '.5em')
      .attr('text-anchor', 'middle')
      .text(d => d.data.account.split(':').pop())
      .style('opacity', 0)
      .call(makeAccountLink);

    this.update();
    return this;
  }

  update() {
    this.width = parseInt(container.style('width'), 10);
    this.height = Math.min(this.width / 2.5, 400);
    this.svg.attr('width', this.width).attr('height', this.height);
    this.treemap.size([this.width, this.height]);

    this.treemap(this.root);

    function labelOpacity(d) {
      const length = this.getComputedTextLength();
      return d.x1 - d.x0 > length + 4 && d.y1 - d.y0 > 14 ? 1 : 0;
    }

    this.selections.cells.attr('transform', d => `translate(${d.x0},${d.y0})`);

    this.selections.cells
      .select('rect')
      .attr('width', d => d.x1 - d.x0)
      .attr('height', d => d.y1 - d.y0);

    this.selections.cells
      .select('text')
      .attr('x', d => (d.x1 - d.x0) / 2)
      .attr('y', d => (d.y1 - d.y0) / 2)
      .style('opacity', labelOpacity);
  }
}

class SunburstChart extends BaseChart {
  constructor(svg) {
    super();
    this.svg = svg;
    this.margin.left = 10;

    this.x = scaleLinear().range([0, 2 * Math.PI]);
    this.y = scaleSqrt();
    this.partition = partition();
    this.arc = arc()
      .startAngle(d => this.x(d.x0))
      .endAngle(d => this.x(d.x1))
      .innerRadius(d => this.y(d.y0))
      .outerRadius(d => this.y(d.y1));
    this.width = 500;
    this.height = 250;

    this.canvas = this.svg
      .attr('class', 'sunburst')
      .append('g')
      .on('mouseleave', d => this.mouseLeave(d));
  }

  draw(data) {
    // Bounding circle underneath the sunburst
    this.canvas
      .append('circle')
      .style('opacity', 0)
      .attr('r', this.radius());

    this.selections.accountLabel = this.canvas
      .append('text')
      .attr('class', 'account')
      .attr('text-anchor', 'middle');
    this.selections.balanceLabel = this.canvas
      .append('text')
      .attr('class', 'balance')
      .attr('dy', '1.2em')
      .attr('text-anchor', 'middle');

    this.root = data;
    this.partition(this.root);

    this.selections.paths = this.canvas
      .selectAll('path')
      .data(this.root.descendants())
      .enter()
      .filter(d => !d.data.dummy && d.depth)
      .append('path')
      .attr('fill-rule', 'evenodd')
      .style('fill', d => scales.sunburst(d.data.account))
      .on('mouseover', d => this.mouseOver(d))
      .call(makeAccountLink);

    this.update();
    this.setLabel(this.root);
    return this;
  }

  update() {
    this.canvas.attr(
      'transform',
      `translate(${this.width / 2 + this.margin.left},${this.height / 2 +
        this.margin.top})`,
    );
    this.svg
      .attr('width', this.width + this.margin.left + this.margin.right)
      .attr('height', this.height + this.margin.top + this.margin.bottom);

    this.y.range([0, this.radius()]);

    this.selections.paths = this.canvas
      .selectAll('path')
      .filter(d => !d.data.dummy && d.depth)
      .attr('d', this.arc);
  }

  radius() {
    return Math.min(this.width, this.height) / 2;
  }

  setLabel(d) {
    this.selections.balanceLabel.text(this.labelText(d));
    this.selections.accountLabel.text(d.data.account).call(makeAccountLink);
  }

  // Fade all but the current sequence
  mouseOver(d) {
    this.setLabel(d);

    // Only highlight segments that are ancestors of the current segment.
    this.selections.paths
      .interrupt()
      .style('opacity', 0.5)
      // check if d.account starts with node.account
      .filter(node => d.data.account.lastIndexOf(node.data.account, 0) === 0)
      .style('opacity', 1);
  }

  // Restore everything to full opacity when moving off the visualization.
  mouseLeave() {
    this.selections.paths
      .transition()
      .duration(1000)
      .style('opacity', 1);
    this.setLabel(this.root);
  }
}

class BarChart extends BaseChart {
  constructor(svg) {
    super();
    this.svg = svg;

    this.x0 = scaleBand().padding(0.1);
    this.x1 = scaleBand();
    this.y = scaleLinear();
    this.selections = {};
    this.maxColumnWidth = 100;

    this.xAxis = axisBottom(this.x0).tickSizeOuter(0);

    this.yAxis = axisLeft(this.y).tickFormat(formatCurrencyShort);

    this.canvas = this.svg.classed('barchart', true).append('g');
    this.selections.xAxis = this.canvas.append('g').attr('class', 'x axis');
    this.selections.yAxis = this.canvas.append('g').attr('class', 'y axis');
  }

  draw(data) {
    this.x0.domain(data.map(d => d.label));
    this.x1.domain(data[0].values.map(d => d.name));

    this.y.domain([
      Math.min(0, min(data, d => min(d.values, x => x.value))),
      Math.max(0, max(data, d => max(d.values, x => x.value))),
    ]);

    this.selections.groups = this.canvas
      .selectAll('.group')
      .data(data)
      .enter()
      .append('g')
      .attr('class', 'group')
      .call(addTooltip, this.tooltipText);

    this.selections.groupboxes = this.selections.groups
      .append('rect')
      .attr('class', 'group-box');

    this.selections.axisgroupboxes = this.selections.groups
      .append('rect')
      .on('click', d => {
        setTimeFilter(d.date);
      })
      .attr('class', 'axis-group-box');

    this.selections.bars = this.selections.groups
      .selectAll('.bar')
      .data(d => d.values)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .style('fill', d => scales.currencies(d.name));

    this.selections.budgets = this.selections.groups
      .selectAll('.budget')
      .data(d => d.values)
      .enter()
      .append('rect')
      .attr('class', 'budget');

    this.update();
    return this;
  }

  update() {
    const screenWidth =
      parseInt(container.style('width'), 10) -
      this.margin.left -
      this.margin.right;
    const maxWidth = this.selections.groups.size() * this.maxColumnWidth;
    const offset = this.margin.left + Math.max(0, screenWidth - maxWidth) / 2;

    this.width = Math.min(screenWidth, maxWidth);
    this.height = 250 - this.margin.top - this.margin.bottom;

    this.y.range([this.height, 0]);
    this.x0.range([0, this.width], 0.1);
    this.x1.range([0, this.x0.bandwidth()]);

    this.svg
      .attr('width', screenWidth + this.margin.left + this.margin.right)
      .attr('height', this.height + this.margin.top + this.margin.bottom);
    this.canvas.attr('transform', `translate(${offset},${this.margin.top})`);

    this.yAxis.tickSize(-this.width, 0);
    this.selections.xAxis.attr('transform', `translate(0,${this.height})`);

    this.xAxis.tickValues(this.filterTicks(this.x0.domain()));
    this.selections.xAxis.call(this.xAxis);
    this.selections.yAxis.call(this.yAxis);

    this.selections.groups.attr(
      'transform',
      d => `translate(${this.x0(d.label)},0)`,
    );

    this.selections.groupboxes
      .attr('width', this.x0.bandwidth())
      .attr('height', this.height);

    this.selections.axisgroupboxes
      .attr('width', this.x0.bandwidth())
      .attr('height', this.margin.bottom)
      .attr('transform', `translate(0,${this.height})`);

    this.selections.budgets
      .attr('width', this.x1.bandwidth())
      .attr('x', d => this.x1(d.name))
      .attr('y', d => this.y(Math.max(0, d.budget)))
      .attr('height', d => Math.abs(this.y(d.budget) - this.y(0)));

    this.selections.bars
      .attr('width', this.x1.bandwidth())
      .attr('x', d => this.x1(d.name))
      .attr('y', d => this.y(Math.max(0, d.value)))
      .attr('height', d => Math.abs(this.y(d.value) - this.y(0)));

    setLegend(this.x1.domain(), scales.currencies);
  }

  filterTicks(domain) {
    const labelsCount = this.width / 70;
    if (domain.length <= labelsCount) {
      return domain;
    }
    const showIndices = Math.ceil(domain.length / labelsCount);
    return domain.filter((d, i) => i % showIndices === 0);
  }
}

class ScatterPlot extends BaseChart {
  constructor(svg) {
    super();
    this.svg = svg;
    this.margin.left = 70;

    this.x = scaleUtc();
    this.y = scalePoint().padding(1);

    this.xAxis = axisBottom(this.x).tickSizeOuter(0);

    this.yAxis = axisLeft(this.y)
      .tickPadding(6)
      .tickFormat(d => d);
  }

  draw(data) {
    this.data = data;
    this.x.domain(extent(data, d => d.date));
    this.y.domain(data.map(d => d.type));

    this.canvas = this.svg.classed('scatterplot', true).append('g');
    this.selections.xAxis = this.canvas.append('g').attr('class', 'x axis');
    this.selections.yAxis = this.canvas.append('g').attr('class', 'y axis');

    this.selections.dots = this.canvas
      .selectAll('.dot')
      .data(this.data)
      .enter()
      .append('circle')
      .attr('class', 'dot')
      .attr('r', 5)
      .style('fill', d => scales.scatterplot(d.type))
      .call(addTooltip, this.tooltipText);

    this.update();
    return this;
  }

  update() {
    this.width =
      parseInt(container.style('width'), 10) -
      this.margin.left -
      this.margin.right;
    this.height = 250 - this.margin.top - this.margin.bottom;

    this.y.range([this.height, 0]);
    this.x.range([0, this.width]);

    this.svg
      .attr('width', this.width + this.margin.left + this.margin.right)
      .attr('height', this.height + this.margin.top + this.margin.bottom);
    this.canvas.attr(
      'transform',
      `translate(${this.margin.left},${this.margin.top})`,
    );

    this.yAxis.tickSize(-this.width, 0);
    this.selections.xAxis.attr('transform', `translate(0,${this.height})`);

    this.selections.xAxis.call(this.xAxis);
    this.selections.yAxis.call(this.yAxis);
    this.selections.dots
      .attr('cx', d => this.x(d.date))
      .attr('cy', d => this.y(d.type));
  }
}

class LineChart extends BaseChart {
  constructor(svg) {
    super();
    this.svg = svg;

    this.x = scaleUtc();
    this.y = scaleLinear();

    this.xAxis = axisBottom(this.x).tickSizeOuter(0);

    this.yAxis = axisLeft(this.y)
      .tickPadding(6)
      .tickFormat(formatCurrencyShort);

    this.line = line()
      .x(d => this.x(d.date))
      .y(d => this.y(d.value));

    this.canvas = this.svg.classed('linechart', true).append('g');
    this.selections.xAxis = this.canvas.append('g').attr('class', 'x axis');
    this.selections.yAxis = this.canvas.append('g').attr('class', 'y axis');
    this.selections.voronoi = this.canvas.append('g').attr('class', 'voronoi');
  }

  draw(data) {
    this.data = data;
    this.points = merge(data.map(d => d.values));
    this.x.domain([
      min(this.data, s => s.values[0].date),
      max(this.data, s => s.values[s.values.length - 1].date),
    ]);

    // Span y-axis as max minus min value plus 5 percent margin
    const minDataValue = min(this.data, d => min(d.values, x => x.value));
    const maxDataValue = max(this.data, d => max(d.values, x => x.value));
    this.y.domain([
      minDataValue - (maxDataValue - minDataValue) * 0.05,
      maxDataValue + (maxDataValue - minDataValue) * 0.05,
    ]);

    this.selections.lines = this.canvas
      .selectAll('.line')
      .data(data)
      .enter()
      .append('path')
      .attr('class', 'line')
      .style('stroke', d => scales.currencies(d.name));

    this.selections.dots = this.canvas
      .selectAll('g.dot')
      .data(data)
      .enter()
      .append('g')
      .attr('class', 'dot')
      .selectAll('circle')
      .data(d => d.values)
      .enter()
      .append('circle')
      .attr('r', 3)
      .style('fill', d => scales.currencies(d.name));

    this.selections.voronoi
      .selectAll('path')
      .data(this.points)
      .enter()
      .append('path')
      .on('mouseenter', d => {
        tooltip.style('opacity', 1).html(this.tooltipText(d.data));
      })
      .on('mousemove', d => {
        const matrix = this.canvas.node().getScreenCTM();
        tooltip
          .style('left', `${this.x(d.data.date) + matrix.e}px`)
          .style('top', `${this.y(d.data.value) + matrix.f + -15}px`);
      })
      .on('mouseleave', () => {
        tooltip.style('opacity', 0);
      });

    this.update();
    return this;
  }

  update() {
    this.width =
      parseInt(container.style('width'), 10) -
      this.margin.left -
      this.margin.right;
    this.height = 250 - this.margin.top - this.margin.bottom;

    this.y.range([this.height, 0]);
    this.x.range([0, this.width]);

    this.svg
      .attr('width', this.width + this.margin.left + this.margin.right)
      .attr('height', this.height + this.margin.top + this.margin.bottom);
    this.canvas.attr(
      'transform',
      `translate(${this.margin.left},${this.margin.top})`,
    );

    this.yAxis.tickSize(-this.width, 0);
    this.selections.xAxis.attr('transform', `translate(0,${this.height})`);

    this.selections.xAxis.call(this.xAxis);
    this.selections.yAxis.call(this.yAxis);
    this.selections.dots
      .attr('cx', d => this.x(d.date))
      .attr('cy', d => this.y(d.value));
    this.selections.lines.attr('d', d => this.line(d.values));

    let paths;
    try {
      const delaunay = Delaunay.from(
        this.points,
        d => this.x(d.date),
        d => this.y(d.value),
      );
      const polygons = delaunay
        .voronoi([0, 0, this.width, this.height])
        .cellPolygons();
      paths = this.points.map(d => ({ path: polygons.next().value, data: d }));
    } catch (error) {
      paths = [];
    }
    this.selections.voronoi
      .selectAll('path')
      .data(paths)
      .filter(d => d.path !== undefined)
      .attr('d', d => `M${d.path.join('L')}Z`);

    setLegend(this.data.map(d => d.name), scales.currencies);
  }
}

class SunburstChartContainer extends BaseChart {
  constructor(svg) {
    super();
    this.svg = svg.attr('class', 'sunburst');
    this.sunbursts = [];
    this.canvases = [];
  }

  draw(data) {
    this.setSize();
    this.currencies = Object.keys(data);

    this.currencies.forEach((currency, i) => {
      const canvas = this.svg
        .append('g')
        .attr(
          'transform',
          `translate(${(this.width * i) / this.currencies.length},0)`,
        );

      const sunburst = new SunburstChart(canvas)
        .setWidth(this.width / this.currencies.length)
        .setHeight(500)
        .set(
          'labelText',
          d =>
            `${formatCurrency(
              d.data.balance_children[currency] || 0,
            )} ${currency}`,
        )
        .draw(data[currency]);

      this.canvases.push(canvas);
      this.sunbursts.push(sunburst);
    });

    return this;
  }

  setSize() {
    this.width = container.node().offsetWidth;
    this.svg.attr('width', this.width).attr('height', 500);
  }

  update() {
    this.setSize();
    this.sunbursts.forEach((singleChart, i) => {
      singleChart
        .setWidth(this.width / this.currencies.length)
        .setHeight(500)
        .update();
      this.canvases[i].attr(
        'transform',
        `translate(${(this.width * i) / this.currencies.length},0)`,
      );
    });
  }
}

class HierarchyContainer extends BaseChart {
  constructor(svg) {
    super();
    this.svg = svg;
    this.canvas = this.svg.append('g');
    this.has_mode_setting = true;
  }

  draw(data) {
    this.data = data;
    this.currencies = Object.keys(data);
    this.setSize();

    const mode = $('#chart-form input[name=mode]:checked').value;
    const currency = setSelect('#chart-currency', this.currencies);
    this.canvas.html('');

    if (this.currencies.length === 0) {
      this.canvas
        .append('text')
        .text('Chart is empty.')
        .attr('text-anchor', 'middle')
        .attr('x', this.width / 2)
        .attr('y', 160 / 2);
    } else if (mode === 'treemap') {
      this.currentChart = new TreeMapChart(this.canvas)
        .set(
          'tooltipText',
          d =>
            `${formatCurrency(d.data.balance[currency])} ${currency}<em>${
              d.data.account
            }</em>`,
        )
        .draw(data[currency]);

      this.has_currency_setting = true;
    } else {
      this.currentChart = new SunburstChartContainer(this.canvas).draw(data);

      this.has_currency_setting = false;
    }

    this.svg.attr('height', this.canvas.attr('height'));

    return this;
  }

  setSize() {
    this.width = container.node().offsetWidth;
    this.svg.attr('width', this.width);
  }

  update() {
    this.draw(this.data);
    if (this.currentChart) {
      this.currentChart.update();
    }
  }
}

class ChartSwitcher {
  constructor() {
    this.state = {};
  }

  // After a page load, reset the chart switcher with new data.
  reset(renderers) {
    container = select('#chart-container');
    container.html('');

    this.renderers = renderers;
    this.charts = {};
    this.currentChart = undefined;

    // Chart controls
    $$('#chart-form input[name=mode]').forEach(el => {
      el.addEventListener('change', () => {
        this.state.mode = el.value;
        this.show(this.state.id);
      });
    });
    $('#chart-currency').addEventListener('change', this.update.bind(this));

    // Switch between charts
    $$('#chart-labels label').forEach(label => {
      label.addEventListener('click', () => {
        this.show(label.getAttribute('for'));
      });
    });

    if (this.state.mode) {
      $(`#mode-${this.state.mode}`).checked = true;
    }
    // Show the same chart as last time (or call .update() to show the first one).
    if (this.state.id && this.renderers[this.state.id]) {
      this.show(this.state.id);
    } else {
      this.update();
    }
  }

  // Update the current chart (or render the first one if there is none).
  update() {
    if ($('#charts').classList.contains('hide-charts')) return;
    if (!this.currentChart) {
      const firstLabel = $('#chart-labels label:first-child');
      if (firstLabel) {
        this.show(firstLabel.getAttribute('for'));
      }
    } else {
      this.currentChart.update();
    }
  }

  // Show the chart with the given id.
  show(id) {
    if ($('#charts').classList.contains('hide-charts')) return;
    // If the chart has not been rendered yet, do so now.
    if (!this.charts[id]) {
      const svg = container.append('svg').attr('id', id);
      this.charts[id] = this.renderers[id](svg);
    }
    this.currentChart = this.charts[id];
    this.state.id = id;

    $$('#charts svg').forEach(el => {
      el.classList.add('hidden');
    });
    $(`#${id}`).classList.remove('hidden');

    $('#chart-legend').innerHTML = '';

    $$('#chart-labels .selected').forEach(el => {
      el.classList.remove('selected');
    });
    $(`#chart-labels [for=${id}]`).classList.add('selected');

    this.currentChart.update();

    $('#chart-currency').classList.toggle(
      'hidden',
      !this.currentChart.has_currency_setting,
    );
    $('#chart-mode').classList.toggle(
      'hidden',
      !this.currentChart.has_mode_setting,
    );
  }
}

const chartSwitcher = new ChartSwitcher();

// Get the list of operating currencies, adding in the current conversion
// currency.
function getOperatingCurrencies() {
  const conversion = $('#conversion').value;
  if (
    conversion &&
    conversion !== 'at_cost' &&
    conversion !== 'at_value' &&
    conversion !== 'units' &&
    window.favaAPI.options.operating_currency.indexOf(conversion) === -1
  ) {
    const currencies = window.favaAPI.options.operating_currency.slice();
    currencies.push(conversion);
    return currencies;
  }
  return window.favaAPI.options.operating_currency;
}

e.on('page-init', () => {
  tooltip = select('#tooltip');
  window.addEventListener('resize', chartSwitcher.update.bind(chartSwitcher));

  scales.treemap.domain(window.favaAPI.accounts);
  scales.sunburst.domain(window.favaAPI.accounts);
  window.favaAPI.options.commodities.sort();
  scales.currencies.domain(window.favaAPI.options.commodities);
});

e.on('page-loaded', () => {
  tooltip.style('opacity', 0);

  if (!$('#charts')) return;

  const renderers = {};

  // Go through the chart data and prepare it for rendering. For each chart,
  // add a label, and a function renderers[id] that will render the chart.
  JSON.parse($('#chart-data').innerHTML).forEach((chart, index) => {
    const id = `${chart.type}-${index}`;
    switch (chart.type) {
      case 'balances': {
        const series = window.favaAPI.options.commodities
          .map(c => ({
            name: c,
            values: chart.data
              .filter(d => !(d.balance[c] === undefined))
              .map(d => ({
                name: c,
                date: new Date(d.date),
                value: Number(d.balance[c]),
              })),
          }))
          .filter(d => d.values.length);

        renderers[id] = svg =>
          new LineChart(svg)
            .set(
              'tooltipText',
              d =>
                `${formatCurrency(d.value)} ${d.name}<em>${dateFormat.day(
                  d.date,
                )}</em>`,
            )
            .draw(series);
        break;
      }
      case 'commodities': {
        const series = [
          {
            name: chart.label,
            values: chart.prices.map(d => ({
              name: chart.label,
              date: new Date(d[0]),
              value: d[1],
            })),
          },
        ];

        if (series[0].values.length) {
          renderers[id] = svg =>
            new LineChart(svg)
              .set(
                'tooltipText',
                d =>
                  `1 ${chart.base} = ${formatCurrency(d.value)} ${
                    chart.quote
                  }<em>${dateFormat.day(d.date)}</em>`,
              )
              .draw(series);
        }
        break;
      }
      case 'bar': {
        const currentDateFormat = dateFormat[$('#chart-interval').value];
        const operatingCurrencies = getOperatingCurrencies();
        const series = chart.series.map(d => ({
          values: operatingCurrencies.map(name => ({
            name,
            value: +d.balance[name] || 0,
            budget: +d.budgets[name] || 0,
          })),
          date: new Date(d.date),
          label: currentDateFormat(new Date(d.date)),
        }));

        renderers[id] = svg =>
          new BarChart(svg)
            .set('tooltipText', d => {
              let text = '';
              d.values.forEach(a => {
                text += `${formatCurrency(a.value)} ${a.name}`;
                if (a.budget) {
                  text += ` / ${formatCurrency(a.budget)} ${a.name}`;
                }
                text += '<br>';
              });
              text += `<em>${d.label}</em>`;
              return text;
            })
            .draw(series);
        break;
      }
      case 'scatterplot': {
        const series = chart.events.map(d => ({
          type: d.type,
          date: new Date(d.date),
          description: d.description,
        }));

        renderers[id] = svg =>
          new ScatterPlot(svg)
            .set(
              'tooltipText',
              d => `${d.description}<em>${dateFormat.day(d.date)}</em>`,
            )
            .draw(series);

        break;
      }
      case 'hierarchy': {
        addInternalNodesAsLeaves(chart.root);
        const roots = {};

        const operatingCurrencies = getOperatingCurrencies();
        operatingCurrencies.forEach(currency => {
          const currencyHierarchy = hierarchy(chart.root)
            .sum(d => d.balance[currency] * chart.modifier)
            .sort((a, b) => b.value - a.value);
          if (currencyHierarchy.value !== 0) {
            roots[currency] = currencyHierarchy;
          }
        });

        renderers[id] = svg => new HierarchyContainer(svg).draw(roots);

        break;
      }
      default:
        break;
    }
    if (renderers[id]) {
      select('#chart-labels')
        .append('label')
        .attr('for', id)
        .html(chart.label);
    }
  });

  chartSwitcher.reset(renderers);
});

e.on('button-click-toggle-chart', () => {
  const hideCharts = $('#charts').classList.toggle('hide-charts');
  const url = new URL(window.location.href);
  if (hideCharts) {
    url.searchParams.set('charts', false);
  } else {
    url.searchParams.delete('charts');
    chartSwitcher.update();
  }
  router.navigate(url.toString(), false);
});
