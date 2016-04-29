const d3 = require('d3');
const URI = require('urijs');

const helpers = require('./helpers');

var container;
const treemapColorScale = d3.scale.category20c();
const sunburstColorScale = d3.scale.category20c();
const currencyColorScale = d3.scale.category10();
const scatterColorScale = d3.scale.category10();
const timeFilterFormatStrings = {
      'year':    'YYYY',
      'quarter': 'YYYY-Qq',
      'day':     'YYYY-MM-DD',
      'week':    'YYYY-Www',
      'month':   'YYYY-MM',
}

function addInternalNodesAsLeaves(node) {
    $.each(node.children, function(i, o) {
        addInternalNodesAsLeaves(o);
    });
    if (node.children && node.children.length) {
        var copy = $.extend({}, node)
        copy.children = null;
        copy.dummy = true;
        node.children.push(copy);
        node.balance = {};
    }
};

function makeAccountLink(selection) {
    selection
        .on('click', function(d) {
            window.location = accountUrl.replace('REPLACEME', d.account);
            d3.event.stopPropagation()
        })
}

function addTooltip(selection, tooltipText) {
    selection
        .on('mouseenter', function(d) { tooltip.style('opacity', 1).html(tooltipText(d)); })
        .on('mousemove', function(d) { tooltip.style('left', d3.event.pageX  + 'px').style('top', (d3.event.pageY - 15 )+ 'px') })
        .on('mouseleave', function(d) { tooltip.style('opacity', 0); })
}

function timeFilter(date) {
    var e = $.Event('keyup');
    e.which = 13;
    $("#filter-time input[type=search]")
        .val(date.formatWithString(timeFilterFormatStrings[window.interval]))
        .trigger(e);
}

function addLegend(svg, domain, colorScale) {
    var legend = svg.selectAll('.legend')
        .data(domain)
      .enter().append('g')
        .attr('class', 'legend')

    legend.append('rect')
        .attr('x', -18)
        .attr('width', 18)
        .attr('height', 18)
        .style('fill', function(d) { return colorScale(d); });

    legend.append('text')
        .attr('x', -24)
        .attr('y', 9)
        .attr('dy', '.35em')
        .style('text-anchor', 'end')
        .text(function(d) { return d; });

    return legend
}

function treeMapChart() {
    var width, height;
    var x = d3.scale.linear();
    var y = d3.scale.linear();
    var treemap = d3.layout.treemap()
        .sort(function(a,b) { return a.value - b.value; });
    var zoomBehavior = d3.behavior.zoom();
    var div, svg, root, current_node, cells, leaves, tooltipText;

    function setSize() {
        width = parseInt(container.style('width'), 10);
        height = Math.min(width / 2.5, 400);
        svg
            .attr('width', width)
            .attr('height', height)
        treemap.size([width, height])
        x.range([0, width]);
        y.range([0, height]);
    }

    function chart(div) {
        svg = div.append("svg").attr('class', 'treemap')
        setSize();
        root = div.datum();

        zoomBehavior
            .on('zoomend', function(d) {
                var scale = d3.event.target.scale();
                // click
                if (scale == 1) {
                    zoom(current_node == d.parent ? root : d.parent, 200);
                // zoom in
                } else if (scale > 1) {
                    zoom(d.parent, 200);
                // zoom out
                } else if (scale < 1) {
                    zoom(root, 200);
                }
                d3.event.target.scale(1);
            })

        cells = svg.selectAll('g')
            .data(treemap.nodes(root))
          .enter().append('g')
            .call(zoomBehavior)
            .call(addTooltip, tooltipText)

        leaves = cells.filter(function(d) { return (d.value); })
        if (leaves.empty()) { div.html('<p>Chart is empty.</p>'); };

        leaves.append('rect')
            .attr('fill', function(d) {
                if (d.dummy) { var d = d.parent; }
                return d.parent == root || !d.parent ? treemapColorScale(d.account) : treemapColorScale(d.parent.account);
            })

        leaves.append("text")
            .attr("dy", ".5em")
            .attr("text-anchor", "middle")
            .text(function(d) { return d.account.split(':').pop(); })
            .style('opacity', 0)
            .call(makeAccountLink)

        zoom(root, 0);
    }

    chart.value = function(f) {
        treemap.value(f);
        return chart;
    }

    chart.tooltipText = function(f) {
        tooltipText = f;
        return chart;
    }

    chart.update = function() {
        setSize();
        zoom(current_node, 0);
    }

    function zoom(d, duration) {
        treemap(root);

        var kx = width / d.dx,
            ky = height / d.dy;
        x.domain([d.x, d.x + d.dx]);
        y.domain([d.y, d.y + d.dy]);

        var t = cells.transition()
            .duration(duration)
            .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

        t.select("rect")
            .attr("width", function(d) { return kx * d.dx; })
            .attr("height", function(d) { return ky * d.dy; })

        t.select("text")
            .attr("x", function(d) { return kx * d.dx / 2; })
            .attr("y", function(d) { return ky * d.dy / 2; })
            .style("opacity", function(d) { d.w = this.getComputedTextLength(); return (kx* d.dx > d.w + 4 && ky * d.dy > 14) ? 1 : 0; });

        current_node = d;
    }

    return chart;
}

function sunburstChart() {
    var width, height;
    var x = d3.scale.linear().range([0, 2 * Math.PI]);
    var y = d3.scale.sqrt();
    var div, svg;
    var partition = d3.layout.partition();
    var root, labels, account_label, balance_label, labelText, paths;

    function setSize() {
        width = parseInt(div.style('width'), 10);
        radius = Math.min(width, height) / 2;

        svg.attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');
        div.select('svg')
            .attr('width', width)
            .attr('height', height);

        y.range([0, radius])
    }

    function chart(div_) {
        div = div_;

        svg = div.append('svg').attr('class', 'sunburst').append('g');
        setSize();

        // Bounding circle underneath the sunburst, to make it easier to detect
        // when the mouse leaves the parent g.
        svg.append('circle')
            .style('opacity', 0)
            .attr('r', radius)

        account_label = svg.append('text')
            .attr('class', 'account')
            .attr('text-anchor', 'middle')
        balance_label = svg.append('text')
            .attr('class', 'balance')
            .attr('dy', '1.2em')
            .attr('text-anchor', 'middle')
        labels = svg.selectAll('text')

        var arc = d3.svg.arc()
            .startAngle(function(d) { return x(d.x); })
            .endAngle(function(d) { return x(d.x + d.dx); })
            .innerRadius(function(d) { return y(d.y); })
            .outerRadius(function(d) { return y(d.y + d.dy); });

        // For efficiency, filter nodes to keep only those large enough to see.
        // Also, ignore dummy nodes and root.
        root = div.datum()
        var nodes = partition.nodes(root)
            .filter(function(d) {
                return (d.dx > 0.005 && !d.dummy && d.depth); // 0.005 radians = 0.29 degrees
            });

        paths = svg.selectAll('path')
            .data(nodes)
          .enter().append('path')
            .attr('d', arc)
            .attr('fill-rule', 'evenodd')
            .style('fill', function(d) { return sunburstColorScale(d.account); })
            .on('mouseover', mouseOver)
            .call(makeAccountLink)

        setLabel(root);
        // Add the mouseleave handler to the bounding circle.
        svg.on('mouseleave', mouseLeave);
    }

    chart.labelText = function(f) {
        labelText = f;
        return chart;
    }

    chart.diameter = function(d) {
        height = d;
        return chart;
    }

    chart.value = function(f) {
        partition.value(f);
        return chart;
    }

    function setLabel(d) {
        balance_label.text(labelText(d));
        account_label
            .text(d.account)
            .call(makeAccountLink)
    }


    // Fade all but the current sequence
    function mouseOver(d) {
        setLabel(d);

        // Only highlight segments that are ancestors of the current segment.
        paths
            .interrupt()
            .style('opacity', 0.5)
            .filter(function(node) {
                // check if d.account starts with node.account
                return (d.account.lastIndexOf(node.account, 0) === 0);
            })
            .style('opacity', 1);
    }

    // Restore everything to full opacity when moving off the visualization.
    function mouseLeave(d) {
        paths
            .transition()
            .duration(1000)
            .style('opacity', 1)
        setLabel(root);
    }

    chart.update = function() {
        setSize();
    }

    return chart;
}

function sunburstChartContainer() {
    var sunburstContainers = [];
    var sunbursts = [];
    var currencies;

    function sunburstChartContainer(container, currencies_, diameter, root) {
        addInternalNodesAsLeaves(root);
        currencies = currencies_;
        $.each(currencies, function(i, currency) {
            var id = container.node().id + '-' + currency;
            var div = container.append('div')
                .attr('id', id)
                .style('width', container.node().offsetWidth / currencies.length + 'px')
                .style('z-index', '1')
                .style('float', 'left')
                .style('position', 'relative');
            var sunburst = sunburstChart()
                .diameter(diameter)
                .value(function(d) { return d.balance[currency]; })
                .labelText(function(d) {
                    return helpers.formatCurrency(d.balance_children[currency] || 0) + ' ' + currency;
                })
            div
                .datum(root)
                .call(sunburst)

            sunburstContainers.push(div);
            sunbursts.push(sunburst);
        });
    }

    sunburstChartContainer.update = function() {
        $.each(sunburstContainers, function(i, div) {
            div.style('width', container.node().offsetWidth / currencies.length + 'px')
        });

        $.each(sunbursts, function(i, chart) {
            chart.update();
        });
    }

    return sunburstChartContainer;
}

function barChart() {
    var margin = {top: 10, right: 10, bottom: 20, left: 30};
    var width, height;
    var x0 = d3.scale.ordinal();
    var x1 = d3.scale.ordinal();
    var y = d3.scale.linear();
    var div, svg, tooltipText;
    var selections = {};

    var xAxis = d3.svg.axis()
        .scale(x0)
        .outerTickSize(0)
        .orient('bottom');

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient('left')
        .tickFormat(d3.format('.2s'));

    function setSize() {
        width = parseInt(container.style('width'), 10) - margin.left - margin.right,
        height = 250 - margin.top - margin.bottom;

        y.range([height, 0]);
        x0.rangeRoundBands([0, width], .1);
        x1.rangeRoundBands([0, x0.rangeBand()]);

        svg
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom);
        canvas.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

        yAxis.tickSize(-width, 0)
        selections.xAxis.attr('transform', 'translate(0,' + height + ')')
    }

    function setData(data) {
        x0.domain(data.map(function(d) { return d.label; }));
        x1.domain(data[0].values.map(function(d) { return d.name; }));
        y.domain([
            Math.min(0, d3.min(data, function(d) { return d3.min(d.values, function(d) { return d.value }); })),
            Math.max(0, d3.max(data, function(d) { return d3.max(d.values, function(d) { return d.value }); }))
        ]);
    }

    function filterTicks(domain) {
        var labelsCount = width / 70;
        if (domain.length <= labelsCount) {
            return domain;
        }
        var show_indices = Math.ceil(domain.length / labelsCount)
        return domain.filter(function(d, i) {
            return (i % show_indices) === 0; });
    }

    function resize() {
        xAxis.tickValues(filterTicks(x0.domain()))
        selections.xAxis.call(xAxis);
        selections.yAxis.call(yAxis);

        selections.groups
            .attr('transform', function(d) { return 'translate(' + x0(d.label) + ',0)'; })

        selections.groupboxes
            .attr('width', x0.rangeBand())
            .attr('height', height)

        selections.bars = selections.groups.selectAll('.bar')
            .attr('width', x1.rangeBand())
            .attr('x', function(d ) { return x1(d.name); })
            .attr('y', function(d) { return y(Math.max(0, d.value)); })
            .attr('height', function(d) { return Math.abs(y(d.value) - y(0)); })

        selections.legend
            .attr('transform', function(d, i) { return 'translate(' + width + ',' + i * 20 + ')'; });
    }


    function chart(svg_) {
        svg = svg_;
        canvas = svg.attr('class', 'barchart').append('g')
        selections.xAxis = canvas.append('g').attr('class', 'x axis')
        selections.yAxis = canvas.append('g').attr('class', 'y axis')

        setSize();
        setData(svg.datum());

        selections.groups = canvas.selectAll('.group')
            .data(svg.datum())
          .enter().append('g')
            .attr('class', 'group')
            .call(addTooltip, tooltipText)
            .on('click', function(d) { timeFilter(d.date) })

        selections.groupboxes = selections.groups.append('rect')
            .attr('class', 'group-box')

        selections.bars = selections.groups.selectAll('.bar')
            .data(function(d) { return d.values; })
          .enter().append('rect')
            .attr('class', 'bar')
            .style('fill', function(d) { return currencyColorScale(d.name); })

        selections.legend = addLegend(canvas, x1.domain(), currencyColorScale)

        resize();
    }

    chart.tooltipText = function(f) {
        tooltipText = f;
        return chart;
    }

    chart.update = function() {
        setSize();
        resize();
    }

    return chart;
}

function scatterPlot() {
    var margin = {top: 10, right: 10, bottom: 20, left: 50};
    var width, height;
    var x = d3.time.scale();
    var y = d3.scale.ordinal();
    var div, svg, tooltipText;
    var selections = {};

    var xAxis = d3.svg.axis()
        .scale(x)
        .outerTickSize(0)
        .orient('bottom');

    var yAxis = d3.svg.axis()
        .scale(y)
        .tickPadding(6)
        .orient('left')
        .tickFormat(function(d) { return d; });

    function setSize() {
        width = parseInt(container.style('width'), 10) - margin.left - margin.right,
        height = 250 - margin.top - margin.bottom;

        y.rangePoints([height, 0], 1);
        x.range([0, width]);

        div.select('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom);
        svg.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

        yAxis.tickSize(-width, 0);
        selections.xAxis.attr('transform', 'translate(0,' + height + ')')
    }

    function setData(data) {
        x.domain(d3.extent(data, function(d) { return d.date; }));
        y.domain(data.map(function(d) { return d.type; }));
    }

    function resize() {
        selections.xAxis.call(xAxis);
        selections.yAxis.call(yAxis);
        selections.dots
            .attr("cx", function(d) { return x(d.date); })
            .attr("cy", function(d) { return y(d.type); })
    }

    function chart(div_) {
        div = div_;
        svg = div.append('svg').attr('class', 'scatterplot').append('g')
        selections.xAxis = svg.append('g').attr('class', 'x axis')
        selections.yAxis = svg.append('g').attr('class', 'y axis')

        setSize();
        setData(div.datum());

        selections.dots = svg.selectAll(".dot")
            .data(div.datum())
          .enter().append("circle")
            .attr("class", "dot")
            .attr("r", 5)
            .style("fill", function(d) { return scatterColorScale(d.type);})
            .call(addTooltip, tooltipText)

        resize();
    }

    chart.tooltipText = function(f) {
        tooltipText = f;
        return chart;
    }

    chart.update = function() {
        setSize();
        resize();
    }

    return chart;
}

function lineChart() {
    var margin = {top: 10, right: 10, bottom: 20, left: 30};
    var width = 500 - margin.left - margin.right,
        height = 250 - margin.top - margin.bottom;
    var x = d3.time.scale();
    var y = d3.scale.linear();
    var canvas, tooltipText, matrix;
    var selections = {};

    var xAxis = d3.svg.axis()
        .scale(x)
        .outerTickSize(0)
        .orient('bottom');

    var yAxis = d3.svg.axis()
        .scale(y)
        .tickPadding(6)
        .orient('left')
        .tickFormat(d3.format('.2s'));

    var line = d3.svg.line()
        .x(function(d) { return x(d.date); })
        .y(function(d) { return y(d.value); });

    var voronoi = d3.geom.voronoi()
        .x(function(d) { return x(d.date); })
        .y(function(d) { return y(d.value); });

    function setSize() {
        width = parseInt(container.style('width'), 10) - margin.left - margin.right,

        matrix = canvas.node().getScreenCTM();
        y.range([height, 0]);
        x.range([0, width]);
        voronoi.clipExtent([[0, 0], [width, height]])

        svg
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom);
        canvas.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

        yAxis.tickSize(-width, 0);
        selections.xAxis.attr('transform', 'translate(0,' + height + ')')
    }

    function setData(data) {
        x.domain([
            d3.min(data, function(s) { return s.values[0].date; }),
            d3.max(data, function(s) { return s.values[s.values.length - 1].date; })
        ]);
        y.domain([
            Math.min(0, d3.min(data, function(d) { return d3.min(d.values, function(d) { return d.value }); })),
            Math.max(0, d3.max(data, function(d) { return d3.max(d.values, function(d) { return d.value }); }))
        ]);
    }

    function resize() {
        selections.xAxis.call(xAxis);
        selections.yAxis.call(yAxis);
        selections.dots
            .attr('cx', function(d) { return x(d.date); })
            .attr('cy', function(d) { return y(d.value); })
        selections.lines
            .attr('d', function(d) { return line(d.values); })

        selections.voronoi.selectAll('path')
            .data(voronoi(rollupData(svg.datum())))
            .attr('d', function(d) { return "M" + d.join("L") + "Z"; })
    }

    function rollupData(data) {
        return d3.nest()
            .key(function(d) { return x(d.date) + ',' + y(d.value); })
            .rollup(function(d) { return d[0]; })
            .entries(d3.merge(data.map(function(d) { return d.values; })))
            .map(function(d) { return d.values; } );
    }

    function chart(svg_) {
        svg = svg_;
        canvas = svg.attr('class', 'linechart').append('g')
        selections.xAxis = canvas.append('g').attr('class', 'x axis')
        selections.yAxis = canvas.append('g').attr('class', 'y axis')
        selections.voronoi = canvas.append('g').attr('class', 'voronoi');

        setData(svg.datum());
        setSize();

        selections.lines = canvas.selectAll('.line')
            .data(svg.datum())
          .enter().append('path')
            .attr('class', 'line')
            .style('stroke', function(d) { return scatterColorScale(d.name);})

        selections.dots = canvas.selectAll('g.dot')
            .data(svg.datum())
          .enter().append('g')
            .attr('class', 'dot').selectAll('circle')
            .data(function(d) { return d.values; })
          .enter().append('circle')
            .attr('r', 3)
            .style('fill', function(d) { return scatterColorScale(d.name);})

        selections.voronoi.selectAll('path')
            .data(voronoi(rollupData(svg.datum())))
           .enter().append('path')
            .attr('d', function(d) { return "M" + d.join("L") + "Z"; })
            .on('mouseenter', function(d) {  tooltip.style('opacity', 1).html(tooltipText(d.point)); })
            .on('mousemove', function(d) { tooltip.style('left', (x(d.point.date) + matrix.e)  + 'px').style('top', (y(d.point.value) + matrix.f - 15 )+ 'px') })
            .on('mouseleave', function(d) { tooltip.style('opacity', 0); })

        resize();
    }

    chart.tooltipText = function(f) {
        tooltipText = f;
        return chart;
    }

    chart.update = function() {
        setSize();
        resize();
    }

    return chart;
}

module.exports.initCharts = function() {
    container = d3.select('#chart-container');
    container.html('');
    var labels = d3.select('#chart-labels');
    window.charts = {}
    window.tooltip = d3.select('body').append('div').attr('id', 'tooltip')

    function chartContainer(id, label) {
        var div = container.append('div')
            .attr('class', 'chart')
            .attr('id', id)

        labels.append('label')
            .attr('for', id)
            .html(label)

        return div;
    }

    $.each(window.chartData, function(index, chart) {
        chart.id = chart.type + '-' + index;
        switch(chart.type) {
            case 'balances':
                var div = chartContainer(chart.id, chart.label);
                var linechart = lineChart()
                    .tooltipText(function(d) {
                        return d.value + ' ' + d.name  + '<em>' + d.date.formatWithString('YYYY-MM-DD') + '</em>'; })

                var series = operating_currencies.map(function(c) {
                    return {
                        'name': c,
                        'values': chart.data.filter(function(d) { return !(d.balance[c] === undefined); })
                            .map(function(d) {
                            return {
                                'name': c,
                                'date': new Date(d.date),
                                'value': d.balance[c],
                            };
                        })
                    }
                });
                div.append('svg')
                    .datum(series)
                    .call(linechart)

                window.charts[chart.id] = linechart;
                break;
            case 'commodities':
                var div = chartContainer(chart.id, chart.label);
                var linechart = lineChart()
                    .tooltipText(function(d) {
                        return '1 ' + chart.base + ' =  ' + d.value + ' ' + chart.quote + '<em>' + d.date.formatWithString('YYYY-MM-DD') + '</em>'; })

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
                div.append('svg')
                    .datum(series)
                    .call(linechart)

                window.charts[chart.id] = linechart;
                break;
            case 'bar':
                var div = chartContainer(chart.id, chart.label);
                var barchart = barChart()
                    .tooltipText(function(d) {
                        var text = '';
                        $.each(d.values, function(i, a) {
                            text += a.value + ' ' +  a.name + '<br>';
                        });
                        text += '<em>' + d.label + '</em>';
                        return text; })

                chart.interval_totals.forEach(function(d) {
                    d.values = operating_currencies.map(function(name) {
                        return {name: name, value: +d.totals[name] || 0};
                    });
                    d.date = new Date(d.begin_date);
                    d.label = d.date.formatWithString(chart.date_format)
                });

                div.append('svg')
                    .datum(chart.interval_totals)
                    .call(barchart)

                window.charts[chart.id] = barchart;
                break;
            case 'scatterplot':
                var div = chartContainer(chart.id, chart.label);
                var scatterplot = scatterPlot()
                    .tooltipText(function(d) { return d.description + '<em>' + d.date + '</em>'; })

                div
                    .datum(chart.events)
                    .call(scatterplot)

                window.charts[chart.id] = scatterplot;
                break;
            case 'treemap': {
                addInternalNodesAsLeaves(chart.root);
                $.each(window.operating_currencies, function(i, currency) {
                    chart.id = "treemap-" + index + '-' + currency;

                    var div = chartContainer(chart.id, chart.label + ' (' + currency + ')');
                    var treemap = treeMapChart()
                        .value(function(d) { return d.balance[currency] * chart.modifier; })
                        .tooltipText(function(d) { return d.balance[currency] + ' ' + currency  + '<em>' + d.account + '</em>'; })

                    div
                        .datum(chart.root)
                        .call(treemap)

                    window.charts[chart.id] = treemap;
                })
                break;
            }
            case 'sunburst':
                chart.id = 'sunburst-' + index;
                var container = chartContainer(chart.id, chart.label);

                var scContainer = sunburstChartContainer();
                scContainer(container, window.operating_currencies, chart.diameter, chart.root);
                window.charts[chart.id] = scContainer;
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
        var shouldShow = ($(this).val() == 'Show charts');
        $('#chart-container, #chart-labels, #chart-interval').toggleClass('hidden', !shouldShow);
        $(this).val(shouldShow ? 'Hide charts' : 'Show charts');
    });

    if ($('select#chart-interval').length) {
        $('select#chart-interval').on('change', function() {
            window.location = URI(window.location)
                .setQuery('interval', this.value)
                .toString();
        });
    }
}
