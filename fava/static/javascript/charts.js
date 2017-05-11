import { extent, max, merge, min } from 'd3-array';
import { axisLeft, axisBottom } from 'd3-axis';
import { format } from 'd3-format';
import { utcFormat } from 'd3-time-format';
import { hierarchy, partition, treemap } from 'd3-hierarchy';
import { scaleBand, scaleLinear, scaleOrdinal, scalePoint,
  scaleSqrt, scaleUtc, schemeCategory10, schemeCategory20c } from 'd3-scale';
import { event, select } from 'd3-selection';
import { arc, line } from 'd3-shape';
import { schemeSet3 } from 'd3-scale-chromatic';
import { voronoi } from 'd3-voronoi';
import 'd3-transition';

import { $, $$, _ } from './helpers';

const treemapColorScale = scaleOrdinal(schemeSet3);
const sunburstColorScale = scaleOrdinal(schemeCategory20c);
const currencyColorScale = scaleOrdinal(schemeCategory10);
const scatterColorScale = scaleOrdinal(schemeCategory10);

const formatCurrencyWithComma = format(',.2f');
const formatCurrencyWithoutComma = format('.2f');
function formatCurrency(number) {
  let str = '';
  if (window.favaAPI.options.render_commas) {
    str = formatCurrencyWithComma(number);
  } else {
    str = formatCurrencyWithoutComma(number);
  }
  if (window.favaAPI.favaOptions.incognito) {
    str = str.replace(/[0-9]/g, 'X');
  }
  return str;
}

const formatCurrencyShortDefault = format('.2s');
function formatCurrencyShort(number) {
  let str = formatCurrencyShortDefault(number);
  if (window.favaAPI.favaOptions.incognito) {
    str = str.replace(/[0-9]/g, 'X');
  }
  return str;
}

const dateFormat = {
  year: utcFormat('%Y'),
  quarter(date) {
    return `${date.getUTCFullYear()}Q${Math.floor(date.getUTCMonth() / 3) + 1}`;
  },
  month: utcFormat('%b %Y'),
  week: utcFormat('%YW%W'),
  day: utcFormat('%Y-%m-%d'),
};

let container;
let tooltip;
let charts;

const timeFilterDateFormat = {
  year: utcFormat('%Y'),
  quarter(date) {
    return `${date.getUTCFullYear()}Q${Math.floor(date.getUTCMonth() / 3) + 1}`;
  },
  month: utcFormat('%Y-%m'),
  week: utcFormat('%Y-W%W'),
  day: utcFormat('%Y-%m-%d'),
};

function addInternalNodesAsLeaves(node) {
  node.children.forEach((o) => {
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

function makeAccountLink(selection) {
  selection
    .on('click', (d) => {
      window.location = window.favaAPI.accountURL.replace('REPLACEME', d.data.account);
      event.stopPropagation();
    });
}

function addTooltip(selection, tooltipText) {
  selection
    .on('mouseenter', (d) => {
      tooltip.style('opacity', 1).html(tooltipText(d));
    })
    .on('mousemove', () => {
      tooltip.style('left', `${event.pageX}px`).style('top', `${event.pageY - 15}px`);
    })
    .on('mouseleave', () => {
      tooltip.style('opacity', 0);
    });
}

function timeFilter(date) {
  $('#time-filter').value = timeFilterDateFormat[$('#chart-interval').value](date);
  $('#filter-form').dispatchEvent(new Event('submit'));
}

function addLegend(domain, colorScale) {
  const legend = select('#chart-legend').selectAll('span.legend')
    .data(domain)
    .enter()
    .append('span')
    .attr('class', 'legend');

  legend.append('span')
    .attr('class', 'color')
    .style('background', d => colorScale(d));

  legend.append('span')
    .attr('class', 'name')
    .html(d => d);

  return legend;
}

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

    this.selections.cells = this.svg.selectAll('g')
      .data(this.root.leaves())
      .enter()
      .append('g')
      .call(addTooltip, this.tooltipText);

    if (this.selections.cells.empty()) {
      this.selections.empty = this.canvas.append('text')
        .text(_('Chart is empty.'));
    }

    this.selections.cells.append('rect')
      .attr('fill', (d) => {
        const node = d.data.dummy ? d.parent : d;
        if (node.parent === this.root || !node.parent) {
          return treemapColorScale(node.data.account);
        }
        return treemapColorScale(node.parent.data.account);
      });

    this.selections.cells.append('text')
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
    this.svg
        .attr('width', this.width)
        .attr('height', this.height);
    this.treemap.size([this.width, this.height]);

    if (this.selections.empty) {
      this.selections.empty
          .attr('x', this.width / 2)
          .attr('y', this.height / 2);
    }

    this.treemap(this.root);

    function labelOpacity(d) {
      const length = this.getComputedTextLength();
      return ((d.x1 - d.x0) > length + 4 && (d.y1 - d.y0) > 14) ? 1 : 0;
    }

    this.selections.cells
      .attr('transform', d => `translate(${d.x0},${d.y0})`);

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

    this.canvas = this.svg.attr('class', 'sunburst').append('g')
      .on('mouseleave', d => this.mouseLeave(d));
  }

  draw(data) {
    // Bounding circle underneath the sunburst
    this.canvas.append('circle')
      .style('opacity', 0)
      .attr('r', this.radius());

    this.selections.accountLabel = this.canvas.append('text')
      .attr('class', 'account')
      .attr('text-anchor', 'middle');
    this.selections.balanceLabel = this.canvas.append('text')
      .attr('class', 'balance')
      .attr('dy', '1.2em')
      .attr('text-anchor', 'middle');

    this.root = data;
    this.partition(this.root);

    this.selections.paths = this.canvas.selectAll('path')
        .data(this.root.descendants())
        .enter()
        .filter(d => ((d.x1 - d.x0) > 0.005 && !d.data.dummy && d.depth))
      .append('path')
        .attr('fill-rule', 'evenodd')
        .style('fill', d => sunburstColorScale(d.data.account))
        .on('mouseover', d => this.mouseOver(d))
        .call(makeAccountLink);

    this.update();
    this.setLabel(this.root);
    return this;
  }

  update() {
    this.canvas.attr('transform', `translate(${(this.width / 2) + this.margin.left},${(this.height / 2) + this.margin.top})`);
    this.svg
      .attr('width', this.width + this.margin.left + this.margin.right)
      .attr('height', this.height + this.margin.top + this.margin.bottom);

    this.y.range([0, this.radius()]);

    this.selections.paths = this.canvas.selectAll('path')
      .filter(d => ((d.x1 - d.x0) > 0.005 && !d.data.dummy && d.depth))
      .attr('d', this.arc);
  }

  radius() {
    return Math.min(this.width, this.height) / 2;
  }

  setLabel(d) {
    if (this.selections.paths.empty()) {
      this.selections.accountLabel
        .text(_('Chart is empty.'));
    } else {
      this.selections.balanceLabel
        .text(this.labelText(d));
      this.selections.accountLabel
        .text(d.data.account)
        .call(makeAccountLink);
    }
  }

  // Fade all but the current sequence
  mouseOver(d) {
    this.setLabel(d);

    // Only highlight segments that are ancestors of the current segment.
    this.selections.paths
      .interrupt()
      .style('opacity', 0.5)
      // check if d.account starts with node.account
      .filter(node => (d.data.account.lastIndexOf(node.data.account, 0) === 0))
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

    this.xAxis = axisBottom(this.x0)
      .tickSizeOuter(0);

    this.yAxis = axisLeft(this.y)
      .tickFormat(formatCurrencyShort);

    this.canvas = this.svg.classed('barchart', true).append('g');
    this.selections.xAxis = this.canvas.append('g').attr('class', 'x axis');
    this.selections.yAxis = this.canvas.append('g').attr('class', 'y axis');
  }

  draw(data) {
    this.x0.domain(data.map(d => d.label));
    this.x1.domain(data[0].values.map(d => d.name));

    this.y.domain([
      Math.min(0, min(data, d => min(d.values, e => e.value))),
      Math.max(0, max(data, d => max(d.values, e => e.value))),
    ]);

    this.selections.groups = this.canvas.selectAll('.group')
        .data(data)
      .enter()
      .append('g')
        .attr('class', 'group')
        .call(addTooltip, this.tooltipText);

    this.selections.groupboxes = this.selections.groups.append('rect')
      .attr('class', 'group-box');

    this.selections.axisgroupboxes = this.selections.groups.append('rect')
      .on('click', (d) => {
        timeFilter(d.date);
      })
      .attr('class', 'axis-group-box');

    this.selections.bars = this.selections.groups.selectAll('.bar')
        .data(d => d.values)
        .enter()
      .append('rect')
        .attr('class', 'bar')
        .style('fill', d => currencyColorScale(d.name));

    this.selections.budgets = this.selections.groups.selectAll('.budget')
        .data(d => d.values)
        .enter()
      .append('rect')
        .attr('class', 'budget');

    this.update();
    return this;
  }

  update() {
    const screenWidth = parseInt(container.style('width'), 10) - this.margin.left - this.margin.right;
    const maxWidth = this.selections.groups.size() * this.maxColumnWidth;
    const offset = this.margin.left + (Math.max(0, screenWidth - maxWidth) / 2);

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

    this.selections.groups
      .attr('transform', d => `translate(${this.x0(d.label)},0)`);

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

    addLegend(this.x1.domain(), currencyColorScale);
  }

  filterTicks(domain) {
    const labelsCount = this.width / 70;
    if (domain.length <= labelsCount) {
      return domain;
    }
    const showIndices = Math.ceil(domain.length / labelsCount);
    return domain.filter((d, i) => (i % showIndices) === 0);
  }
}

class ScatterPlot extends BaseChart {
  constructor(svg) {
    super();
    this.svg = svg;
    this.margin.left = 70;

    this.x = scaleUtc();
    this.y = scalePoint().padding(1);

    this.xAxis = axisBottom(this.x)
      .tickSizeOuter(0);

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

    this.selections.dots = this.canvas.selectAll('.dot')
        .data(this.data)
      .enter()
      .append('circle')
        .attr('class', 'dot')
        .attr('r', 5)
        .style('fill', d => scatterColorScale(d.type))
        .call(addTooltip, this.tooltipText);

    this.update();
    return this;
  }

  update() {
    this.width = parseInt(container.style('width'), 10) - this.margin.left - this.margin.right;
    this.height = 250 - this.margin.top - this.margin.bottom;

    this.y.range([this.height, 0]);
    this.x.range([0, this.width]);

    this.svg
      .attr('width', this.width + this.margin.left + this.margin.right)
      .attr('height', this.height + this.margin.top + this.margin.bottom);
    this.canvas.attr('transform', `translate(${this.margin.left},${this.margin.top})`);

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

    this.xAxis = axisBottom(this.x)
      .tickSizeOuter(0);

    this.yAxis = axisLeft(this.y)
      .tickPadding(6)
      .tickFormat(formatCurrencyShort);

    this.line = line()
      .x(d => this.x(d.date))
      .y(d => this.y(d.value));

    this.voronoi = voronoi()
      .x(d => this.x(d.date))
      .y(d => this.y(d.value));

    this.canvas = this.svg.classed('linechart', true).append('g');
    this.selections.xAxis = this.canvas.append('g').attr('class', 'x axis');
    this.selections.yAxis = this.canvas.append('g').attr('class', 'y axis');
    this.selections.voronoi = this.canvas.append('g').attr('class', 'voronoi');
  }

  draw(data) {
    this.data = data;
    this.x.domain([
      min(this.data, s => s.values[0].date),
      max(this.data, s => s.values[s.values.length - 1].date),
    ]);
    this.y.domain([
      Math.min(0, min(this.data, d => min(d.values, e => e.value))),
      Math.max(0, max(this.data, d => max(d.values, e => e.value))),
    ]);

    this.selections.lines = this.canvas.selectAll('.line')
        .data(data)
      .enter()
      .append('path')
        .attr('class', 'line')
        .style('stroke', d => currencyColorScale(d.name));

    this.selections.dots = this.canvas.selectAll('g.dot')
        .data(data)
        .enter()
      .append('g')
        .attr('class', 'dot')
      .selectAll('circle')
        .data(d => d.values)
        .enter()
      .append('circle')
        .attr('r', 3)
        .style('fill', d => currencyColorScale(d.name));

    this.selections.voronoi.selectAll('path')
        .data(this.voronoi.polygons(merge(data.map(d => d.values))))
        .enter()
      .append('path')
        .filter(d => d !== undefined)
        .on('mouseenter', (d) => {
          tooltip.style('opacity', 1).html(this.tooltipText(d.data));
        })
        .on('mousemove', (d) => {
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
    this.width = parseInt(container.style('width'), 10) - this.margin.left - this.margin.right;
    this.height = 250 - this.margin.top - this.margin.bottom;

    this.y.range([this.height, 0]);
    this.x.range([0, this.width]);
    this.voronoi.size([this.width, this.height]);

    this.svg
      .attr('width', this.width + this.margin.left + this.margin.right)
      .attr('height', this.height + this.margin.top + this.margin.bottom);
    this.canvas.attr('transform', `translate(${this.margin.left},${this.margin.top})`);

    this.yAxis.tickSize(-this.width, 0);
    this.selections.xAxis.attr('transform', `translate(0,${this.height})`);

    this.selections.xAxis.call(this.xAxis);
    this.selections.yAxis.call(this.yAxis);
    this.selections.dots
      .attr('cx', d => this.x(d.date))
      .attr('cy', d => this.y(d.value));
    this.selections.lines
      .attr('d', d => this.line(d.values));

    this.selections.voronoi.selectAll('path')
        .data(this.voronoi.polygons(merge(this.data.map(d => d.values))))
        .filter(d => d !== undefined)
        .attr('d', d => `M${d.join('L')}Z`);

    addLegend(this.data.map(d => d.name), currencyColorScale);
  }
}

class SunburstChartContainer extends BaseChart {
  constructor(svg) {
    super();
    this.svg = svg;
    this.svg.attr('class', 'sunburst');

    this.sunbursts = [];
    this.canvases = [];
  }

  draw(data) {
    this.setSize();

    this.currencies.forEach((currency, i) => {
      const canvas = this.svg.append('g')
        .attr('transform', `translate(${(this.width * i) / this.currencies.length},0)`);

      const sunburst = new SunburstChart(canvas)
        .setWidth(this.width / this.currencies.length)
        .setHeight(500)
        .set('labelText', d => `${formatCurrency(d.data.balance_children[currency] || 0)} ${currency}`)
        .draw(data[currency]);

      this.canvases.push(canvas);
      this.sunbursts.push(sunburst);
    });

    return this;
  }

  setSize() {
    this.width = container.node().offsetWidth;
    this.svg
      .attr('width', this.width)
      .attr('height', 500);
  }

  update() {
    this.setSize();
    this.sunbursts.forEach((singleChart, i) => {
      singleChart
        .setWidth(this.width / this.currencies.length)
        .setHeight(500)
        .update();
      this.canvases[i]
        .attr('transform', `translate(${(this.width * i) / this.currencies.length},0)`);
    });
  }
}

class HierarchyContainer extends BaseChart {
  constructor(svg) {
    super();
    this.svg = svg;

    this.has_mode_setting = true;
    this.currentCurrency = '';
    this.currentMode = '';

    this.canvas = this.svg.append('g');
  }

  draw(data) {
    this.data = data;
    this.setSize();

    const mode = $('#chart-form input[name=mode]:checked').value;
    const currency = $('#chart-currency').value;

    if (mode === 'treemap' && (mode !== this.currentMode || currency !== this.currentCurrency)) {
      this.canvas.html('');

      this.currentChart = new TreeMapChart(this.canvas)
        .set('tooltipText', d => `${formatCurrency(d.data.balance[currency])} ${currency}<em>${d.data.account}</em>`)
        .draw(data[currency]);

      this.has_currency_setting = true;
      this.currentCurrency = currency;
      $('#chart-currency').classList.remove('hidden');
    }

    if (mode === 'sunburst' && mode !== this.currentMode) {
      this.canvas
          .html('');

      this.currentChart = new SunburstChartContainer(this.canvas)
          .set('currencies', this.currencies)
          .draw(data);

      this.has_currency_setting = false;
      $('#chart-currency').classList.add('hidden');
    }
    this.currentMode = mode;

    this.svg
      .attr('height', this.canvas.attr('height'));

    return this;
  }

  setSize() {
    this.width = container.node().offsetWidth;
    this.svg
      .attr('width', this.width);
  }

  update() {
    this.setSize();
    this.draw(this.data);
    this.currentChart.update();
  }
}

let currentChart;
function updateChart() {
  if (!$('#charts').classList.contains('hidden')) {
    currentChart.update();
  }
}

function getOperatingCurrencies() {
  const conversion = $('#conversion').value;
  if (conversion && conversion !== 'at_cost' && conversion !== 'at_value'
      && window.favaAPI.options.operating_currency.indexOf(conversion) === -1) {
    const currencies = window.favaAPI.options.operating_currency.slice();
    currencies.push(conversion);
    return currencies;
  }
  return window.favaAPI.options.operating_currency;
}

export default function initCharts() {
  tooltip = select('#tooltip');
  tooltip.style('opacity', 0);

  window.removeEventListener('resize', updateChart);
  if (!$('#charts')) {
    return;
  }

  container = select('#chart-container');
  container.html('');
  charts = {};

  function chartContainer(id, label) {
    const svg = container.append('svg')
      .attr('class', 'chart')
      .attr('id', id);

    select('#chart-labels').append('label')
      .attr('for', id)
      .html(label);

    return svg;
  }

  const chartData = JSON.parse($('#chart-data').innerHTML);
  chartData.forEach((chart, index) => {
    const chartId = `${chart.type}-${index}`;
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
                    value: d.balance[c],
                  })),
            }))
            .filter(d => d.values.length);

        charts[chartId] = new LineChart(chartContainer(chartId, chart.label))
          .set('tooltipText', d => `${formatCurrency(d.value)} ${d.name}<em>${dateFormat.day(d.date)}</em>`)
          .draw(series);

        break;
      }
      case 'commodities': {
        const series = [{
          name: chart.label,
          values: chart.prices.map(d => ({
            name: chart.label,
            date: new Date(d[0]),
            value: d[1],
          })),
        }];

        charts[chartId] = new LineChart(chartContainer(chartId, chart.label))
          .set('tooltipText', d => `1 ${chart.base} = ${formatCurrency(d.value)} ${chart.quote}<em>${dateFormat.day(d.date)}</em>`)
          .draw(series);

        break;
      }
      case 'bar': {
        const series = chart.interval_totals.map(d => ({
          values: getOperatingCurrencies().map(name => ({
            name,
            value: +d.totals[name] || 0,
            budget: +d.budgets[name] || 0,
          })),
          date: new Date(d.begin_date),
          label: dateFormat[$('#chart-interval').value](new Date(d.begin_date)),
        }));

        charts[chartId] = new BarChart(chartContainer(chartId, chart.label))
          .set('tooltipText', (d) => {
            let text = '';
            d.values.forEach((a) => {
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

        charts[chartId] = new ScatterPlot(chartContainer(chartId, chart.label))
          .set('tooltipText', d => `${d.description}<em>${dateFormat.day(d.date)}</em>`)
          .draw(series);

        break;
      }
      case 'hierarchy': {
        addInternalNodesAsLeaves(chart.root);
        const roots = {};

        const operatingCurrencies = getOperatingCurrencies();
        operatingCurrencies.forEach((currency) => {
          roots[currency] = hierarchy(chart.root)
            .sum(d => d.balance[currency] * chart.modifier)
            .sort((a, b) => b.value - a.value);
        });

        charts[chartId] = new HierarchyContainer(chartContainer(chartId, chart.label))
            .set('currencies', operatingCurrencies)
            .draw(roots);

        break;
      }
      default:
        break;
    }
  });

  const labels = $('#chart-labels');

  // Switch between charts
  $$('label', labels).forEach((label) => {
    label.addEventListener('click', () => {
      // Don't do anything if the charts aren't shown.
      if ($('#charts').classList.contains('hidden')) {
        return;
      }

      const chartId = label.getAttribute('for');
      $$('.charts .chart').forEach((el) => { el.classList.add('hidden'); });
      $(`#${chartId}`).classList.remove('hidden');

      $$('.selected', labels).forEach((el) => { el.classList.remove('selected'); });
      label.classList.add('selected');

      $('#chart-legend').innerHTML = '';

      currentChart = charts[chartId];
      currentChart.update();

      $$('#chart-form input[name=mode]').forEach((el) => { el.addEventListener('change', updateChart); });
      $('#chart-currency').addEventListener('change', updateChart);
      window.addEventListener('resize', updateChart);

      $('#chart-currency').classList.toggle('hidden', !currentChart.has_currency_setting);
      $('#chart-mode').classList.toggle('hidden', !currentChart.has_mode_setting);
    });
  });
  if ($('label:first-child', labels)) {
    $('label:first-child', labels).click();
  }

  const toggleChart = $('#toggle-chart');
  toggleChart.addEventListener('click', () => {
    toggleChart.classList.toggle('hide-charts');
    $('#charts').classList.toggle('hidden', toggleChart.classList.contains('hide-charts'));
    updateChart();
  });
}
