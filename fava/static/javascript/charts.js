import { schemeSet3 } from 'd3-scale-chromatic';

const d3 = require('d3');
const URI = require('urijs');

let container;
const treemapColorScale = d3.scaleOrdinal(schemeSet3);
const sunburstColorScale = d3.scaleOrdinal(d3.schemeCategory20c);
const currencyColorScale = d3.scaleOrdinal(d3.schemeCategory10);
const scatterColorScale = d3.scaleOrdinal(d3.schemeCategory10);

const formatCurrency = d3.format('.2f');
const dateFormat = {
  year: d3.utcFormat('%Y'),
  quarter(date) {
    return `${date.getUTCFullYear()}Q${Math.floor(date.getUTCMonth() / 3) + 1}`;
  },
  month: d3.utcFormat('%b %Y'),
  week: d3.utcFormat('%YW%W'),
  day: d3.utcFormat('%Y-%m-%d'),
};

const timeFilterDateFormat = {
  year: d3.utcFormat('%Y'),
  quarter(date) {
    return `${date.getUTCFullYear()}Q${Math.floor(date.getUTCMonth() / 3) + 1}`;
  },
  month: d3.utcFormat('%Y-%m'),
  week: d3.utcFormat('%Y-W%W'),
  day: d3.utcFormat('%Y-%m-%d'),
};

function addInternalNodesAsLeaves(node) {
  $.each(node.children, (i, o) => {
    addInternalNodesAsLeaves(o);
  });
  if (node.children && node.children.length) {
    const copy = $.extend({}, node);
    copy.children = null;
    copy.dummy = true;
    node.children.push(copy);
    node.balance = {}; // eslint-disable-line no-param-reassign
  }
}

function makeAccountLink(selection) {
  selection
    .on('click', (d) => {
      window.location = window.accountUrl.replace('REPLACEME', d.data.account);
      d3.event.stopPropagation();
    });
}

function addTooltip(selection, tooltipText) {
  selection
    .on('mouseenter', (d) => {
      window.tooltip.style('opacity', 1).html(tooltipText(d));
    })
    .on('mousemove', () => {
      window.tooltip.style('left', `${d3.event.pageX}px`).style('top', `${d3.event.pageY - 15}px`);
    })
    .on('mouseleave', () => {
      window.tooltip.style('opacity', 0);
    });
}

function timeFilter(date) {
  window.location = new URI(window.location)
    .setQuery('time', timeFilterDateFormat[window.interval](date))
    .toString();
}

function addLegend(domain, colorScale) {
  const legend = d3.select('#chart-legend').selectAll('span.legend')
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

function treeMapChart() {
  const x = d3.scaleLinear();
  const y = d3.scaleLinear();
  const treemap = d3.treemap();
  const zoomBehavior = d3.zoom();

  let width;
  let height;
  let svg;
  let root;
  let currentNode;
  let cells;
  let tooltipText;
  let canvas;

  function setSize() {
    width = parseInt(container.style('width'), 10);
    height = Math.min(width / 2.5, 400);
    svg
        .attr('width', width)
        .attr('height', height);
    treemap.size([width, height]);
    x.range([0, width]);
    y.range([0, height]);
  }

  function zoom(node, duration) {
    treemap(root);

    const kx = width / (node.x1 - node.x0);
    const ky = height / (node.y1 - node.y0);
    x.domain([node.x0, node.x1]);
    y.domain([node.y0, node.y1]);

    function labelOpacity(d) {
      const length = this.getComputedTextLength();
      return (kx * (d.x1 - d.x0) > length + 4 && ky * (d.y1 - d.y0) > 14) ? 1 : 0;
    }

    const t = cells.transition()
      .duration(duration)
      .attr('transform', d => `translate(${x(d.x0)},${y(d.y0)})`);

    t.select('rect')
      .attr('width', d => kx * (d.x1 - d.x0))
      .attr('height', d => ky * (d.y1 - d.y0));

    t.select('text')
      .attr('x', d => (kx * (d.x1 - d.x0)) / 2)
      .attr('y', d => (ky * (d.y1 - d.y0)) / 2)
      .style('opacity', labelOpacity);

    currentNode = node;
  }

  function onZoom(d) {
    const scale = d3.event.transform.k;
    // click
    if (scale === 1) {
      zoom(currentNode === d.parent ? root : d.parent, 200);
    } else if (scale > 1) {
      zoom(d.parent, 200);
    } else if (scale < 1) {
      zoom(root, 200);
    }
    this.__zoom = d3.zoomIdentity; // eslint-disable-line no-underscore-dangle
  }

  function chart(svg_) {
    svg = svg_;
    canvas = svg.classed('treemap', true);
    setSize();
    root = svg.datum();
    treemap(root);

    zoomBehavior
      .on('end', onZoom);

    cells = svg.selectAll('g')
      .data(root.leaves())
      .enter()
      .append('g')
      .call(zoomBehavior)
      .call(addTooltip, tooltipText);

    if (cells.empty()) {
      canvas.append('text')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .text('Chart is empty.');
    }

    cells.append('rect')
      .attr('fill', (d) => {
        const node = d.data.dummy ? d.parent : d;
        if (node.parent === root || !node.parent) {
          return treemapColorScale(node.data.account);
        }
        return treemapColorScale(node.parent.data.account);
      });

    cells.append('text')
      .attr('dy', '.5em')
      .attr('text-anchor', 'middle')
      .text(d => d.data.account.split(':').pop())
      .style('opacity', 0)
      .call(makeAccountLink);

    zoom(root, 0);
  }

  chart.tooltipText = (f) => {
    tooltipText = f;
    return chart;
  };

  chart.update = () => {
    setSize();
    zoom(currentNode, 0);
  };

  return chart;
}

function sunburstChart() {
  const margin = {
    top: 10,
    right: 10,
    bottom: 10,
    left: 10,
  };
  const x = d3.scaleLinear().range([0, 2 * Math.PI]);
  const y = d3.scaleSqrt();
  const partition = d3.partition();
  const arc = d3.arc()
    .startAngle(d => x(d.x0))
    .endAngle(d => x(d.x1))
    .innerRadius(d => y(d.y0))
    .outerRadius(d => y(d.y1));

  const selections = {};
  let width = 500;
  let height = 250;
  let svg;
  let canvas;
  let root;
  let labelText;
  let radius;

  function setSize() {
    radius = Math.min(width, height) / 2;

    canvas.attr('transform', `translate(${(width / 2) + margin.left},${(height / 2) + margin.top})`);
    svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.left);

    y.range([0, radius]);
  }

  function resize() {
    selections.paths = canvas.selectAll('path')
      .filter(d => ((d.x1 - d.x0) > 0.005 && !d.data.dummy && d.depth))
      .attr('d', arc);
  }

  function setLabel(d) {
    if (selections.paths.empty()) {
      selections.accountLabel
        .text('Chart is empty.');
    } else {
      selections.balanceLabel
        .text(labelText(d));
      selections.accountLabel
        .text(d.data.account)
        .call(makeAccountLink);
    }
  }

  // Fade all but the current sequence
  function mouseOver(d) {
    setLabel(d);

    // Only highlight segments that are ancestors of the current segment.
    selections.paths
      .interrupt()
      .style('opacity', 0.5)
      // check if d.account starts with node.account
      .filter(node => (d.data.account.lastIndexOf(node.data.account, 0) === 0))
      .style('opacity', 1);
  }

  // Restore everything to full opacity when moving off the visualization.
  function mouseLeave() {
    selections.paths
      .transition()
      .duration(1000)
      .style('opacity', 1);
    setLabel(root);
  }

  function chart(svg_) {
    svg = svg_;
    canvas = svg.attr('class', 'sunburst').append('g')
      .on('mouseleave', mouseLeave);

    setSize();

    // Bounding circle underneath the sunburst
    canvas.append('circle')
      .style('opacity', 0)
      .attr('r', radius);

    selections.accountLabel = canvas.append('text')
      .attr('class', 'account')
      .attr('text-anchor', 'middle');
    selections.balanceLabel = canvas.append('text')
      .attr('class', 'balance')
      .attr('dy', '1.2em')
      .attr('text-anchor', 'middle');

    root = svg.datum();
    partition(root);

    selections.paths = canvas.selectAll('path')
        .data(root.descendants())
        .enter()
        .filter(d => ((d.x1 - d.x0) > 0.005 && !d.data.dummy && d.depth))
      .append('path')
        .attr('fill-rule', 'evenodd')
        .style('fill', d => sunburstColorScale(d.data.account))
        .on('mouseover', mouseOver)
        .call(makeAccountLink);

    resize();
    setLabel(root);
  }

  chart.labelText = (f) => {
    labelText = f;
    return chart;
  };

  chart.height = (d) => {
    height = d - margin.top - margin.bottom;
    return chart;
  };

  chart.width = (d) => {
    width = d - margin.left - margin.right;
    return chart;
  };

  chart.update = () => {
    setSize();
    resize();
  };

  return chart;
}

function barChart() {
  const margin = {
    top: 10,
    right: 10,
    bottom: 30,
    left: 40,
  };
  let width;
  let height;
  const x0 = d3.scaleBand().padding(0.1);
  const x1 = d3.scaleBand();
  const y = d3.scaleLinear();
  let svg;
  let canvas;
  let tooltipText;
  const selections = {};

  const xAxis = d3.axisBottom(x0)
    .tickSizeOuter(0);

  const yAxis = d3.axisLeft(y)
    .tickFormat(d3.format('.2s'));

  function setSize() {
    width = parseInt(container.style('width'), 10) - margin.left - margin.right;
    height = 250 - margin.top - margin.bottom;

    y.range([height, 0]);
    x0.range([0, width], 0.1);
    x1.range([0, x0.bandwidth()]);

    svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);
    canvas.attr('transform', `translate(${margin.left},${margin.top})`);

    yAxis.tickSize(-width, 0);
    selections.xAxis.attr('transform', `translate(0,${height})`);
  }

  function setData(data) {
    x0.domain(data.map(d => d.label));
    x1.domain(data[0].values.map(d => d.name));

    y.domain([
      Math.min(0, d3.min(data, d => d3.min(d.values, e => e.value))),
      Math.max(0, d3.max(data, d => d3.max(d.values, e => e.value))),
    ]);
  }

  function filterTicks(domain) {
    const labelsCount = width / 70;
    if (domain.length <= labelsCount) {
      return domain;
    }
    const showIndices = Math.ceil(domain.length / labelsCount);
    return domain.filter((d, i) => (i % showIndices) === 0);
  }

  function resize() {
    xAxis.tickValues(filterTicks(x0.domain()));
    selections.xAxis.call(xAxis);
    selections.yAxis.call(yAxis);

    selections.groups
      .attr('transform', d => `translate(${x0(d.label)},0)`);

    selections.groupboxes
      .attr('width', x0.bandwidth())
      .attr('height', height);

    selections.bars = selections.groups.selectAll('.bar')
      .attr('width', x1.bandwidth())
      .attr('x', d => x1(d.name))
      .attr('y', d => y(Math.max(0, d.value)))
      .attr('height', d => Math.abs(y(d.value) - y(0)));
  }

  function chart(svg_) {
    svg = svg_;
    canvas = svg.classed('barchart', true).append('g');
    selections.xAxis = canvas.append('g').attr('class', 'x axis');
    selections.yAxis = canvas.append('g').attr('class', 'y axis');

    setSize();
    setData(svg.datum());

    selections.groups = canvas.selectAll('.group')
        .data(svg.datum())
      .enter()
      .append('g')
        .attr('class', 'group')
        .call(addTooltip, tooltipText)
        .on('click', (d) => {
          timeFilter(d.date);
        });

    selections.groupboxes = selections.groups.append('rect')
      .attr('class', 'group-box');

    selections.bars = selections.groups.selectAll('.bar')
        .data(d => d.values)
        .enter()
      .append('rect')
        .attr('class', 'bar')
        .style('fill', d => currencyColorScale(d.name));

    resize();
  }

  chart.tooltipText = (f) => {
    tooltipText = f;
    return chart;
  };

  chart.update = () => {
    setSize();
    resize();
    addLegend(x1.domain(), currencyColorScale);
  };

  return chart;
}

function scatterPlot() {
  const margin = {
    top: 10,
    right: 10,
    bottom: 30,
    left: 70,
  };
  let width;
  let height;
  const x = d3.scaleUtc();
  const y = d3.scalePoint().padding(1);
  let svg;
  let canvas;
  let tooltipText;
  const selections = {};

  const xAxis = d3.axisBottom(x)
    .tickSizeOuter(0);

  const yAxis = d3.axisLeft(y)
    .tickPadding(6)
    .tickFormat(d => d);

  function setSize() {
    width = parseInt(container.style('width'), 10) - margin.left - margin.right;
    height = 250 - margin.top - margin.bottom;

    y.range([height, 0]);
    x.range([0, width]);

    svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);
    canvas.attr('transform', `translate(${margin.left},${margin.top})`);

    yAxis.tickSize(-width, 0);
    selections.xAxis.attr('transform', `translate(0,${height})`);
  }

  function setData(data) {
    x.domain(d3.extent(data, d => d.date));
    y.domain(data.map(d => d.type));
  }

  function resize() {
    selections.xAxis.call(xAxis);
    selections.yAxis.call(yAxis);
    selections.dots
      .attr('cx', d => x(d.date))
      .attr('cy', d => y(d.type));
  }

  function chart(svg_) {
    svg = svg_;
    canvas = svg.classed('scatterplot', true).append('g');
    selections.xAxis = canvas.append('g').attr('class', 'x axis');
    selections.yAxis = canvas.append('g').attr('class', 'y axis');

    setSize();
    setData(svg.datum());

    selections.dots = canvas.selectAll('.dot')
        .data(svg.datum())
      .enter()
      .append('circle')
        .attr('class', 'dot')
        .attr('r', 5)
        .style('fill', d => scatterColorScale(d.type))
        .call(addTooltip, tooltipText);

    resize();
  }

  chart.tooltipText = (f) => {
    tooltipText = f;
    return chart;
  };

  chart.update = () => {
    setSize();
    resize();
  };

  return chart;
}

function lineChart() {
  const margin = {
    top: 10,
    right: 10,
    bottom: 30,
    left: 40,
  };
  let width = 500 - margin.left - margin.right;
  const height = 250 - margin.top - margin.bottom;
  const x = d3.scaleUtc();
  const y = d3.scaleLinear();
  let canvas;
  let tooltipText;
  let matrix;
  let svg;
  const selections = {};

  const xAxis = d3.axisBottom(x)
    .tickSizeOuter(0);

  const yAxis = d3.axisLeft(y)
    .tickPadding(6)
    .tickFormat(d3.format('.2s'));

  const line = d3.line()
    .x(d => x(d.date))
    .y(d => y(d.value));

  const voronoi = d3.voronoi()
    .x(d => x(d.date))
    .y(d => y(d.value));

  function setSize() {
    width = parseInt(container.style('width'), 10) - margin.left - margin.right;
    matrix = canvas.node().getScreenCTM();

    y.range([height, 0]);
    x.range([0, width]);
    voronoi.size([width, height]);

    svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);
    canvas.attr('transform', `translate(${margin.left},${margin.top})`);

    yAxis.tickSize(-width, 0);
    selections.xAxis.attr('transform', `translate(0,${height})`);
  }

  function setData(data) {
    x.domain([
      d3.min(data, s => s.values[0].date),
      d3.max(data, s => s.values[s.values.length - 1].date),
    ]);
    y.domain([
      Math.min(0, d3.min(data, d => d3.min(d.values, e => e.value))),
      Math.max(0, d3.max(data, d => d3.max(d.values, e => e.value))),
    ]);
  }

  function resize() {
    selections.xAxis.call(xAxis);
    selections.yAxis.call(yAxis);
    selections.dots
      .attr('cx', d => x(d.date))
      .attr('cy', d => y(d.value));
    selections.lines
      .attr('d', d => line(d.values));

    selections.voronoi.selectAll('path')
        .data(voronoi.polygons(d3.merge(svg.datum().map(d => d.values))))
        .filter(d => d !== undefined)
        .attr('d', d => `M${d.join('L')}Z`);
  }

  function chart(svg_) {
    svg = svg_;
    canvas = svg.classed('linechart', true).append('g');
    selections.xAxis = canvas.append('g').attr('class', 'x axis');
    selections.yAxis = canvas.append('g').attr('class', 'y axis');
    selections.voronoi = canvas.append('g').attr('class', 'voronoi');

    const data = svg.datum();
    setData(data);
    setSize();

    selections.lines = canvas.selectAll('.line')
        .data(data)
      .enter()
      .append('path')
        .attr('class', 'line')
        .style('stroke', d => currencyColorScale(d.name));

    selections.dots = canvas.selectAll('g.dot')
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

    selections.voronoi.selectAll('path')
        .data(voronoi.polygons(d3.merge(data.map(d => d.values))))
        .enter()
      .append('path')
        .filter(d => d !== undefined)
        .attr('d', d => `M${d.join('L')}Z`)
        .on('mouseenter', (d) => {
          window.tooltip.style('opacity', 1).html(tooltipText(d.data));
        })
        .on('mousemove', (d) => {
          window.tooltip
              .style('left', `${x(d.data.date) + matrix.e}px`)
              .style('top', `${y(d.data.value) + matrix.f + -15}px`);
        })
        .on('mouseleave', () => {
          window.tooltip.style('opacity', 0);
        });

    resize();
  }

  chart.tooltipText = (f) => {
    tooltipText = f;
    return chart;
  };

  chart.update = () => {
    setSize();
    resize();
    addLegend(svg.datum().map(d => d.name), currencyColorScale);
  };

  return chart;
}

function sunburstChartContainer() {
  let width;
  const sunbursts = [];
  const canvases = [];
  let currencies;
  let svg;

  function setSize() {
    width = container.node().offsetWidth;
    svg
      .attr('width', width)
      .attr('height', 500);
  }

  function chart(svg_) {
    svg = svg_;
    svg.attr('class', 'sunburst');
    setSize();

    $.each(currencies, (i, currency) => {
      const sunburst = sunburstChart()
        .width(width / currencies.length)
        .height(500)
        .labelText(d => `${formatCurrency(d.data.balance_children[currency] || 0)} ${currency}`);

      canvases.push(svg.append('g')
        .attr('transform', `translate(${(width * i) / currencies.length},0)`)
        .datum(svg.datum()[currency])
        .call(sunburst));

      sunbursts.push(sunburst);
    });
  }

  chart.update = () => {
    setSize();
    $.each(sunbursts, (i, singleChart) => {
      singleChart
        .width(width / currencies.length)
        .height(500)
        .update();
      canvases[i]
        .attr('transform', `translate(${(width * i) / currencies.length},0)`);
    });
  };

  chart.currencies = (f) => {
    currencies = f;
    return chart;
  };

  return chart;
}

function hierarchyContainer() {
  let width;
  let svg;
  let canvas;
  let currentChart;
  let currentCurrency = '';
  let currentMode = '';
  let currencies;

  function setSize() {
    width = container.node().offsetWidth;
    svg
      .attr('width', width);
  }

  function chart(svg_) {
    svg = svg_;
    setSize();

    canvas = svg.append('g');
  }

  function drawChart() {
    const mode = d3.select('#chart-form input[name=mode]:checked').property('value');
    const currency = d3.select('#chart-currency').property('value');

    if (mode === 'treemap' && (mode !== currentMode || currency !== currentCurrency)) {
      currentChart = treeMapChart()
        .tooltipText(d => `${formatCurrency(d.data.balance[currency])} ${currency}<em>${d.data.account}</em>`); // eslint-disable-line max-len

      canvas
          .html('')
          .datum(svg.datum()[currency])
          .call(currentChart);

      chart.has_currency_setting = true;
      currentCurrency = currency;
      $('#chart-currency').show();
    }

    if (mode === 'sunburst' && mode !== currentMode) {
      currentChart = sunburstChartContainer()
          .currencies(currencies);

      canvas
          .html('')
          .datum(svg.datum())
          .call(currentChart);

      chart.has_currency_setting = false;
      $('#chart-currency').hide();
    }
    chart.has_mode_setting = true;
    currentMode = mode;

    svg
      .attr('height', canvas.attr('height'));
  }

  chart.update = () => {
    setSize();
    drawChart();
    currentChart.update();
  };

  chart.currencies = (f) => {
    currencies = f;
    return chart;
  };

  return chart;
}

module.exports.initCharts = function initCharts() {
  let currentChart;
  container = d3.select('#chart-container');
  container.html('');
  const labels = d3.select('#chart-labels');
  window.charts = {};
  window.tooltip = d3.select('body').append('div').attr('id', 'tooltip');

  function chartContainer(id, label) {
    const svg = container.append('svg')
      .attr('class', 'chart')
      .attr('id', id);

    labels.append('label')
      .attr('for', id)
      .html(label);

    return svg;
  }

  $.each(window.chartData, (index, chart) => {
    const chartId = `${chart.type}-${index}`;
    switch (chart.type) {
      case 'balances': {
        const linechart = lineChart()
          .tooltipText(d => `${formatCurrency(d.value)} ${d.name}<em>${dateFormat.day(d.date)}</em>`); // eslint-disable-line max-len

        const series = window.commodities
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

        chartContainer(chartId, chart.label)
          .datum(series)
          .call(linechart);

        window.charts[chartId] = linechart;
        break;
      }
      case 'commodities': {
        const linechart = lineChart()
          .tooltipText(d => `1 ${chart.base} = ${formatCurrency(d.value)} ${chart.quote}<em>${dateFormat.day(d.date)}</em>`); // eslint-disable-line max-len

        const series = [{
          name: chart.label,
          values: chart.prices.map(d => ({
            name: chart.label,
            date: new Date(d[0]),
            value: d[1],
          })),
        }];

        chartContainer(chartId, chart.label)
          .datum(series)
          .call(linechart);

        window.charts[chartId] = linechart;
        break;
      }
      case 'bar': {
        const barchart = barChart()
          .tooltipText((d) => {
            let text = '';
            $.each(d.values, (i, a) => {
              text += `${formatCurrency(a.value)} ${a.name}<br>`;
            });
            text += `<em>${d.label}</em>`;
            return text;
          });

        const series = chart.interval_totals.map(d => ({
          values: window.operating_currencies.map(name => ({
            name,
            value: +d.totals[name] || 0,
          })),
          date: new Date(d.begin_date),
          label: dateFormat[window.interval](new Date(d.begin_date)),
        }));

        chartContainer(chartId, chart.label)
          .datum(series)
          .call(barchart);

        window.charts[chartId] = barchart;
        break;
      }
      case 'scatterplot': {
        const scatterplot = scatterPlot()
          .tooltipText(d => `${d.description}<em>${dateFormat.day(d.date)}</em>`);

        const series = chart.events.map(d => ({
          type: d.type,
          date: new Date(d.date),
          description: d.description,
        }));

        chartContainer(chartId, chart.label)
          .datum(series)
          .call(scatterplot);

        window.charts[chartId] = scatterplot;
        break;
      }
      case 'hierarchy': {
        addInternalNodesAsLeaves(chart.root);
        const roots = {};

        $.each(window.operating_currencies, (i, currency) => {
          roots[currency] = d3.hierarchy(chart.root)
            .sum(d => d.balance[currency] * chart.modifier)
            .sort((a, b) => b.value - a.value);
        });

        const hierarchy = hierarchyContainer()
            .currencies(window.operating_currencies);

        chartContainer(chartId, `${chart.label}`)
          .datum(roots)
          .call(hierarchy);

        window.charts[chartId] = hierarchy;
        break;
      }
      default:
        break;
    }
  });

  const $labels = $('#chart-labels');
  const $toggleChart = $('#toggle-chart');

  // Switch between charts
  $labels.find('label').click((event) => {
    const chartId = $(event.currentTarget).prop('for');
    $('.charts .chart').addClass('hidden');
    $(`.charts .chart#${chartId}`).removeClass('hidden');

    $labels.find('label').removeClass('selected');
    $(event.currentTarget).addClass('selected');

    $('#chart-legend').html('');

    currentChart = window.charts[chartId];
    currentChart.update();

    d3.selectAll('#chart-form input[name=mode]').on('change', () => { currentChart.update(); });
    d3.select('#chart-currency').on('change', () => { currentChart.update(); });
    d3.select(window).on('resize', () => { currentChart.update(); });

    $('#chart-currency').toggle(!!currentChart.has_currency_setting);
    $('#chart-mode').toggle(!!currentChart.has_mode_setting);
  });
  $labels.find('label:first-child').click();

  $toggleChart.click(() => {
    $toggleChart.toggleClass('hide-charts');
    $('#charts')
        .toggleClass('hidden', $toggleChart.hasClass('hide-charts'));
    currentChart.update();
  });

  $('select#chart-interval').on('change', (event) => {
    window.location = new URI(window.location)
      .setQuery('interval', event.currentTarget.value)
      .toString();
  });
};
