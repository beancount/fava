const d3 = require('d3');
const URI = require('urijs');

let container;
const treemapColorScale = d3.scale.category20c();
const sunburstColorScale = d3.scale.category20c();
const currencyColorScale = d3.scale.category10();
const scatterColorScale = d3.scale.category10();

const formatCurrency = d3.format('.2f');
const dateFormat = {
  year: d3.time.format.utc('%Y'),
  quarter(date) {
    return date.getUTCFullYear() + 'Q' + (Math.floor(date.getUTCMonth() / 3) + 1);
  },
  month: d3.time.format.utc('%b %Y'),
  week: d3.time.format.utc('%YW%W'),
  day: d3.time.format.utc('%Y-%m-%d'),
};

const timeFilterDateFormat = {
  year: d3.time.format.utc('%Y'),
  quarter(date) {
    return date.getUTCFullYear() + '-Q' + (Math.floor(date.getUTCMonth() / 3) + 1);
  },
  month: d3.time.format.utc('%Y-%m'),
  week: d3.time.format.utc('%Y-W%W'),
  day: d3.time.format.utc('%Y-%m-%d'),
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
    node.balance = {};
  }
}

function makeAccountLink(selection) {
  selection
    .on('click', (d) => {
      window.location = window.accountUrl.replace('REPLACEME', d.account);
      d3.event.stopPropagation();
    });
}

function addTooltip(selection, tooltipText) {
  selection
    .on('mouseenter', (d) => {
      window.tooltip.style('opacity', 1).html(tooltipText(d));
    })
    .on('mousemove', () => {
      window.tooltip.style('left', d3.event.pageX + 'px').style('top', (d3.event.pageY - 15) + 'px')
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

function addLegend(svg, domain, colorScale) {
  const legend = svg.selectAll('.legend')
    .data(domain)
    .enter()
    .append('g')
    .attr('class', 'legend');

  legend.append('rect')
    .attr('x', -18)
    .attr('width', 18)
    .attr('height', 18)
    .style('fill', (d) => colorScale(d));

  legend.append('text')
    .attr('x', -24)
    .attr('y', 9)
    .attr('dy', '.35em')
    .style('text-anchor', 'end')
    .text((d) => d);

  return legend;
}

function treeMapChart() {
  let width;
  let height;
  const x = d3.scale.linear();
  const y = d3.scale.linear();
  const treemap = d3.layout.treemap()
    .sort((a, b) => a.value - b.value);
  const zoomBehavior = d3.behavior.zoom();
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

    const kx = width / node.dx;
    const ky = height / node.dy;
    x.domain([node.x, node.x + node.dx]);
    y.domain([node.y, node.y + node.dy]);

    const t = cells.transition()
      .duration(duration)
      .attr('transform', (d) => 'translate(' + x(d.x) + ',' + y(d.y) + ')');

    t.select('rect')
      .attr('width', (d) => kx * d.dx)
      .attr('height', (d) => ky * d.dy);

    t.select('text')
      .attr('x', (d) => kx * d.dx / 2)
      .attr('y', (d) => ky * d.dy / 2)
      .style('opacity', function(d) {
        const length = this.getComputedTextLength();
        return (kx * d.dx > length + 4 && ky * d.dy > 14) ? 1 : 0;
      });

    currentNode = node;
  }

  function chart(svg_) {
    svg = svg_;
    canvas = svg.classed('treemap', true);
    setSize();
    root = svg.datum();

    zoomBehavior
      .on('zoomend', (d) => {
        const scale = d3.event.target.scale();
        // click
        if (scale === 1) {
          zoom(currentNode === d.parent ? root : d.parent, 200);
          // zoom in
        } else if (scale > 1) {
          zoom(d.parent, 200);
          // zoom out
        } else if (scale < 1) {
          zoom(root, 200);
        }
        d3.event.target.scale(1);
      });

    cells = svg.selectAll('g')
      .data(treemap.nodes(root).filter((d) => d.value))
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
        const node = d.dummy ? d.parent : d;
        if (node.parent === root || !node.parent) {
          return treemapColorScale(node.account);
        }
        return treemapColorScale(node.parent.account);
      });

    cells.append('text')
      .attr('dy', '.5em')
      .attr('text-anchor', 'middle')
      .text((d) => d.account.split(':').pop())
      .style('opacity', 0)
      .call(makeAccountLink);

    zoom(root, 0);
  }

  chart.value = (f) => {
    treemap.value(f);
    return chart;
  };

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
  let width = 500;
  let height = 250;
  const x = d3.scale.linear().range([0, 2 * Math.PI]);
  const y = d3.scale.sqrt();
  const partition = d3.layout.partition();
  let svg;
  let canvas;
  let root;
  let labelText;
  const selections = {};
  let radius;

  const arc = d3.svg.arc()
    .startAngle((d) => x(d.x))
    .endAngle((d) => x(d.x + d.dx))
    .innerRadius((d) => y(d.y))
    .outerRadius((d) => y(d.y + d.dy));

  function setSize() {
    radius = Math.min(width, height) / 2;

    canvas.attr('transform', 'translate(' + (width / 2 + margin.left) + ',' + (height / 2 + margin.top) + ')');
    svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.left);

    y.range([0, radius]);
  }

  function resize() {
    root = svg.datum();

    // 0.005 radians = 0.29 degrees
    const nodes = partition.nodes(root)
      .filter((d) => (d.dx > 0.005 && !d.dummy && d.depth));

    selections.paths = canvas.selectAll('path')
      .data(nodes)
      .attr('d', arc);
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

    // For efficiency, filter nodes to keep only those large enough to see.
    // Also, ignore dummy nodes and root.
    root = svg.datum();
    const nodes = partition.nodes(root)
      .filter((d) => (d.dx > 0.005 && !d.dummy && d.depth));

    selections.paths = canvas.selectAll('path')
        .data(nodes)
        .enter()
      .append('path')
        .attr('fill-rule', 'evenodd')
        .style('fill', (d) => sunburstColorScale(d.account))
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

  chart.value = (f) => {
    partition.value(f);
    return chart;
  };

  function setLabel(d) {
    if (selections.paths.empty()) {
      selections.accountLabel
        .text('Chart is empty.');
    } else {
      selections.balanceLabel
        .text(labelText(d));
      selections.accountLabel
        .text(d.account)
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
      .filter((node) => (d.account.lastIndexOf(node.account, 0) === 0))
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

  chart.update = () => {
    setSize();
    resize();
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
    setSize();

    $.each(currencies, function(i, currency) {
      var sunburst = sunburstChart()
        .width(width / currencies.length)
        .height(500)
        .value((d) => d.balance[currency])
        .labelText(function(d) {
          return formatCurrency(d.balance_children[currency] || 0) + ' ' + currency;
        })

      canvases.push(svg.append('g')
        .attr('transform', 'translate(' + width * i / currencies.length + ',0)')
        .datum(svg.datum())
        .call(sunburst));

      sunbursts.push(sunburst);
    });
  }

  chart.update = () => {
    setSize();
    $.each(sunbursts, (i, chart) => {
      chart
        .width(width / currencies.length)
        .height(500)
        .update();
      canvases[i]
        .attr('transform', 'translate(' + width * i / currencies.length + ',0)')
    });
  };

  chart.currencies = (f) => {
    currencies = f;
    return chart;
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
  const x0 = d3.scale.ordinal();
  const x1 = d3.scale.ordinal();
  const y = d3.scale.linear();
  let svg;
  let canvas;
  let tooltipText;
  const selections = {};

  const xAxis = d3.svg.axis()
    .scale(x0)
    .outerTickSize(0)
    .orient('bottom');

  const yAxis = d3.svg.axis()
    .scale(y)
    .orient('left')
    .tickFormat(d3.format('.2s'));

  function setSize() {
    width = parseInt(container.style('width'), 10) - margin.left - margin.right;
    height = 250 - margin.top - margin.bottom;

    y.range([height, 0]);
    x0.rangeRoundBands([0, width], 0.1);
    x1.rangeRoundBands([0, x0.rangeBand()]);

    svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);
    canvas.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    yAxis.tickSize(-width, 0);
    selections.xAxis.attr('transform', 'translate(0,' + height + ')')
  }

  function setData(data) {
    x0.domain(data.map((d) => d.label));
    x1.domain(data[0].values.map((d) => d.name));
    y.domain([
      Math.min(0, d3.min(data, (d) => d3.min(d.values, (e) => e.value))),
      Math.max(0, d3.max(data, (d) => d3.max(d.values, (e) => e.value))),
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
      .attr('transform', (d) => 'translate(' + x0(d.label) + ',0)');

    selections.groupboxes
      .attr('width', x0.rangeBand())
      .attr('height', height);

    selections.bars = selections.groups.selectAll('.bar')
      .attr('width', x1.rangeBand())
      .attr('x', (d) => x1(d.name))
      .attr('y', (d) => y(Math.max(0, d.value)))
      .attr('height', (d) => Math.abs(y(d.value) - y(0)));

    selections.legend
      .attr('transform', (d, i) => 'translate(' + width + ',' + i * 20 + ')');
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
        .data((d) => d.values)
        .enter()
      .append('rect')
        .attr('class', 'bar')
        .style('fill', (d) => currencyColorScale(d.name));

    selections.legend = addLegend(canvas, x1.domain(), currencyColorScale);

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

function scatterPlot() {
  const margin = {
    top: 10,
    right: 10,
    bottom: 30,
    left: 70,
  };
  let width;
  let height;
  const x = d3.time.scale.utc();
  const y = d3.scale.ordinal();
  let svg;
  let canvas;
  let tooltipText;
  const selections = {};

  const xAxis = d3.svg.axis()
    .scale(x)
    .outerTickSize(0)
    .orient('bottom');

  const yAxis = d3.svg.axis()
    .scale(y)
    .tickPadding(6)
    .orient('left')
    .tickFormat((d) => d);

  function setSize() {
    width = parseInt(container.style('width'), 10) - margin.left - margin.right;
    height = 250 - margin.top - margin.bottom;

    y.rangePoints([height, 0], 1);
    x.range([0, width]);

    svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);
    canvas.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    yAxis.tickSize(-width, 0);
    selections.xAxis.attr('transform', 'translate(0,' + height + ')')
  }

  function setData(data) {
    x.domain(d3.extent(data, (d) => d.date));
    y.domain(data.map((d) => d.type));
  }

  function resize() {
    selections.xAxis.call(xAxis);
    selections.yAxis.call(yAxis);
    selections.dots
      .attr('cx', (d) => x(d.date))
      .attr('cy', (d) => y(d.type));
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
        .style('fill', (d) => scatterColorScale(d.type))
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
  const x = d3.time.scale.utc();
  const y = d3.scale.linear();
  let canvas;
  let tooltipText;
  let matrix;
  let svg;
  const selections = {};

  const xAxis = d3.svg.axis()
    .scale(x)
    .outerTickSize(0)
    .orient('bottom');

  const yAxis = d3.svg.axis()
    .scale(y)
    .tickPadding(6)
    .orient('left')
    .tickFormat(d3.format('.2s'));

  const line = d3.svg.line()
    .x((d) => x(d.date))
    .y((d) => y(d.value));

  const voronoi = d3.geom.voronoi()
    .x((d) => x(d.date))
    .y((d) => y(d.value));

  function setSize() {
    width = parseInt(container.style('width'), 10) - margin.left - margin.right;
    matrix = canvas.node().getScreenCTM();

    y.range([height, 0]);
    x.range([0, width]);
    voronoi.clipExtent([
      [0, 0],
      [width, height],
    ]);

    svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);
    canvas.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    yAxis.tickSize(-width, 0);
    selections.xAxis.attr('transform', 'translate(0,' + height + ')')
  }

  function setData(data) {
    x.domain([
      d3.min(data, (s) => s.values[0].date),
      d3.max(data, (s) => s.values[s.values.length - 1].date),
    ]);
    y.domain([
      Math.min(0, d3.min(data, (d) => d3.min(d.values, (e) => e.value))),
      Math.max(0, d3.max(data, (d) => d3.max(d.values, (e) => e.value))),
    ]);
  }

  function resize() {
    selections.xAxis.call(xAxis);
    selections.yAxis.call(yAxis);
    selections.dots
      .attr('cx', function(d) {
        return x(d.date);
      })
      .attr('cy', function(d) {
        return y(d.value);
      })
    selections.lines
      .attr('d', function(d) {
        return line(d.values);
      })

    selections.voronoi.selectAll('path')
      .data(voronoi(rollupData(svg.datum())))
      .attr('d', function(d) {
        return "M" + d.join("L") + "Z";
      })

    selections.legend
      .attr('transform', function(d, i) {
        return 'translate(' + width + ',' + i * 20 + ')';
      });
  }

  function rollupData(data) {
    return d3.nest()
      .key((d) => x(d.date) + ',' + y(d.value))
      .rollup((d) => d[0])
      .entries(d3.merge(data.map((d) => d.values)))
      .map((d) => d.values);
  }

  function chart(svg_) {
    svg = svg_;
    canvas = svg.classed('linechart', true).append('g');
    selections.xAxis = canvas.append('g').attr('class', 'x axis');
    selections.yAxis = canvas.append('g').attr('class', 'y axis');
    selections.voronoi = canvas.append('g').attr('class', 'voronoi');

    setData(svg.datum());
    setSize();

    selections.lines = canvas.selectAll('.line')
        .data(svg.datum())
      .enter()
      .append('path')
        .attr('class', 'line')
        .style('stroke', (d) => currencyColorScale(d.name));

    selections.dots = canvas.selectAll('g.dot')
        .data(svg.datum())
      .enter()
      .append('g')
        .attr('class', 'dot').selectAll('circle')
        .data((d) => d.values)
      .enter()
      .append('circle')
        .attr('r', 3)
        .style('fill', (d) => currencyColorScale(d.name));

    selections.voronoi.selectAll('path')
        .data(voronoi(rollupData(svg.datum())))
      .enter()
      .append('path')
        .attr('d', (d) => "M" + d.join("L") + "Z")
        .on('mouseenter', (d) => {
          window.tooltip.style('opacity', 1).html(tooltipText(d.point));
        })
        .on('mousemove', (d) => {
          window.tooltip
              .style('left', (x(d.point.date) + matrix.e) + 'px')
              .style('top', (y(d.point.value) + matrix.f - 15) + 'px');
        })
        .on('mouseleave', () => {
          window.tooltip.style('opacity', 0);
        });

    selections.legend = addLegend(canvas, svg.datum().map((d) => d.name), currencyColorScale);

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

module.exports.initCharts = function() {
  container = d3.select('#chart-container');
  container.html('');
  var labels = d3.select('#chart-labels');
  window.charts = {}
  window.tooltip = d3.select('body').append('div').attr('id', 'tooltip')

  function chartContainer(id, label) {
    var svg = container.append('svg')
      .attr('class', 'chart')
      .attr('id', id)

    labels.append('label')
      .attr('for', id)
      .html(label)

    return svg;
  }

  $.each(window.chartData, function(index, chart) {
    chart.id = chart.type + '-' + index;
    switch (chart.type) {
      case 'balances':
        var linechart = lineChart()
          .tooltipText(function(d) {
            return formatCurrency(d.value) + ' ' + d.name + '<em>' + dateFormat['day'](d.date) + '</em>';
          })

        var series = window.commodities.map(function(c) {
          return {
            'name': c,
            'values': chart.data.filter(function(d) {
                return !(d.balance[c] === undefined);
              })
              .map(function(d) {
                return {
                  'name': c,
                  'date': new Date(d.date),
                  'value': d.balance[c],
                };
              })
          }
        }).filter(function(d) {
          return d.values.length;
        });

        chartContainer(chart.id, chart.label)
          .datum(series)
          .call(linechart)

        window.charts[chart.id] = linechart;
        break;
      case 'commodities':
        var linechart = lineChart()
          .tooltipText(function(d) {
            return '1 ' + chart.base + ' =  ' + formatCurrency(d.value) + ' ' + chart.quote + '<em>' + dateFormat['day'](d.date) + '</em>';
          })

        var series = [{
          'name': chart.label,
          'values': chart.prices.map(function(d) {
            return {
              'name': chart.label,
              'date': new Date(d[0]),
              'value': d[1],
            };
          })
        }];

        chartContainer(chart.id, chart.label)
          .datum(series)
          .call(linechart)

        window.charts[chart.id] = linechart;
        break;
      case 'bar':
        var barchart = barChart()
          .tooltipText(function(d) {
            var text = '';
            $.each(d.values, function(i, a) {
              text += formatCurrency(a.value) + ' ' + a.name + '<br>';
            });
            text += '<em>' + d.label + '</em>';
            return text;
          })

        chart.interval_totals.forEach(function(d) {
          d.values = window.operating_currencies.map(function(name) {
            return {
              name: name,
              value: +d.totals[name] || 0
            };
          });
          d.date = new Date(d.begin_date);
          d.label = dateFormat[window.interval](d.date)
        });

        chartContainer(chart.id, chart.label)
          .datum(chart.interval_totals)
          .call(barchart)

        window.charts[chart.id] = barchart;
        break;
      case 'scatterplot':
        var scatterplot = scatterPlot()
          .tooltipText(function(d) {
            return d.description + '<em>' + dateFormat['day'](d.date) + '</em>';
          })

        chartContainer(chart.id, chart.label)
          .datum(chart.events.map(function(d) {
            d.date = new Date(d.date);
            return d;
          }))
          .call(scatterplot)

        window.charts[chart.id] = scatterplot;
        break;
      case 'treemap':
        {
          addInternalNodesAsLeaves(chart.root);

          $.each(window.operating_currencies, function(i, currency) {
            chart.id = "treemap-" + index + '-' + currency;

            var treemap = treeMapChart()
              .value(function(d) {
                return d.balance[currency] * chart.modifier;
              })
              .tooltipText(function(d) {
                return formatCurrency(d.balance[currency]) + ' ' + currency + '<em>' + d.account + '</em>';
              })

            chartContainer(chart.id, chart.label + ' (' + currency + ')')
              .datum(chart.root)
              .call(treemap)

            window.charts[chart.id] = treemap;
          })
          break;
        }
      case 'sunburst':
        addInternalNodesAsLeaves(chart.root);

        var sunburst = sunburstChartContainer()
          .currencies(window.operating_currencies)

        chartContainer(chart.id, chart.label)
          .datum(chart.root)
          .call(sunburst);

        window.charts[chart.id] = sunburst;
        break;
      default:
        console.error('Chart-Type "' + chart.type + '" unknown.');
        console.log(chart);
    }
  });

  var $labels = $('#chart-labels');

  // Switch between charts
  $labels.find('label').click(function() {
    var chartId = $(this).prop('for');
    $('.charts .chart').addClass('hidden')
    $('.charts .chart#' + chartId).removeClass('hidden');

    $labels.find('label').removeClass('selected');
    $(this).addClass('selected');

    window.charts[chartId].update();

    d3.select(window).on('resize', function() {
      window.charts[chartId].update();
    })
  });
  $labels.find('label:first-child').click();

  // Toggle charts
  $('#toggle-chart').click(function(event) {
    event.preventDefault();
    var shouldShow = !$(this).hasClass('show-charts');
    $('#chart-container, #chart-labels, #chart-interval').toggleClass('hidden', !shouldShow);
    $(this).toggleClass('show-charts', shouldShow);
  });

  $('select#chart-interval').on('change', function() {
    window.location = URI(window.location)
      .setQuery('interval', this.value)
      .toString();
  });
}
