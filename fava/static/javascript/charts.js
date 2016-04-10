Chartist = require('chartist');
require('chartist-plugin-legend');
require('chartist-plugin-tooltip');
require('./vendor/chartist-plugin-zoom');

var d3 = require('d3');

var helpers = require('./helpers');

var defaultOptions = {
    height: 240,
    chartPadding: { left: 3 },
    axisY: {
        onlyInteger: true,
        position: 'end',
        scaleMinSpace: 15,
        labelInterpolationFnc: helpers.formatCurrency,
        referenceValue: 0,
    },
    plugins: [
        Chartist.plugins.legend(),
        Chartist.plugins.tooltip({
            tooltipFnc: function(meta, value){
                return decodeEntities(meta);
            }
        })
    ]
};

var container;

var colorScale = d3.scale.category20c();

function addInternalNodesAsLeaves(node) {
    $.each(node.children, function(i, o) {
        addInternalNodesAsLeaves(o);
    });
    if (node.children.length) {
        var copy = $.extend({}, node)
        copy.children = null;
        copy.dummy = true;
        node.children.push(copy);
        node.balance = null
    }
};

function treeMapChart() {
    var width, height, kx, ky;
    var x = d3.scale.linear(), y = d3.scale.linear();
    var treemap = d3.layout.treemap()
        .sort(function(a,b) { return a.value - b.value; })
    var transitionDelay = 200;
    var div, svg, root, current_node, cells, leaves, tooltipText;

    function setSize() {
        width = parseInt(container.style('width'), 10);
        height = Math.min(width / 2.5, 400);
        svg
            .attr('width', width)
            .attr('height', height)
        treemap.size([width, height])
    }

    function chart(div) {
        svg = div.append("svg")
            .attr('class', 'treemap')

        setSize();

        root = div.datum()
        cells = svg.selectAll('g')
            .data(treemap.nodes(root))
          .enter().append('g')
            .attr('class', 'cell')
            .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })
            .on('click', function(d) { zoom(current_node == d.parent ? root : d.parent); d3.event.stopPropagation(); })
            .on('mouseenter', function(d) { tooltip.style('opacity', 1).html(tooltipText(d)); })
            .on('mousemove', function(d) { tooltip.style('left', d3.event.pageX  + 'px').style('top', (d3.event.pageY - 15 )+ 'px') })
            .on('mouseleave', function(d) { tooltip.style('opacity', 0); })

        leaves = cells.filter(function(d) { return (d.value); })
        if (leaves.empty()) { div.html('<p>Chart is empty.</p>'); };

        leaves.append('rect')
            .attr('fill', function(d) { return d.parent == root || !d.parent ? colorScale(d.account) : colorScale(d.parent.account) ;})

        leaves.append("text")
            .attr("dy", ".5em")
            .attr("text-anchor", "middle")
            .text(function(d) { return d.account.split(':').pop(); })
            .style('opacity', 0)
            .on('click', function(d) {
                window.location = accountUrl.replace('REPLACEME', d.account);
                d3.event.stopPropagation()
            })

        zoom(root);
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
        transitionDelay = 0;
        setSize();
        zoom(current_node);
        transitionDelay = 200;
    }

    function zoom(d) {
        treemap(root);

        kx =  width / d.dx, ky = height / d.dy;
        x.range([0, width]).domain([d.x, d.x + d.dx]);
        y.range([0, height]).domain([d.y, d.y + d.dy]);

        var t = cells.transition()
            .duration(transitionDelay)
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

var sunburstColorScale = d3.scale.category20c();

function sunburstChart() {
    var width, height;
    var x = d3.scale.linear().range([0, 2 * Math.PI]);
    var y = d3.scale.sqrt();
    var div, vis;
    var partition = d3.layout.partition();
    var root, labels, account_label, balance_label, labelText, paths;

    function setSize() {
        width = parseInt(div.style('width'), 10);
        radius = Math.min(width, height) / 2;

        vis.attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');
        div.select('svg')
            .attr('width', width)
            .attr('height', height);

        y.range([0, radius])
    }
    function chart(div_) {
        div = div_;

        vis = div.append('svg').attr('class', 'sunburst').append('g');
        setSize();

        // Bounding circle underneath the sunburst, to make it easier to detect
        // when the mouse leaves the parent g.
        vis.append('circle')
            .style('opacity', 0)
            .attr('r', radius)

        account_label = vis.append('text')
            .attr('class', 'account')
            .attr('text-anchor', 'middle')
        balance_label = vis.append('text')
            .attr('class', 'balance')
            .attr('dy', '1.2em')
            .attr('text-anchor', 'middle')
        labels = vis.selectAll('text')

        var arc = d3.svg.arc()
            .startAngle(function(d) { return x(d.x); })
            .endAngle(function(d) { return x(d.x + d.dx); })
            .innerRadius(function(d) { return y(d.y); })
            .outerRadius(function(d) { return y(d.y + d.dy); });

        // For efficiency, filter nodes to keep only those large enough to see.
        root = div.datum()
        var nodes = partition.nodes(root)
            .filter(function(d) {
                return (d.dx > 0.005 && !d.dummy); // 0.005 radians = 0.29 degrees
            });

        paths = vis.selectAll('path')
            .data(nodes)
          .enter().append('path')
            .attr('display', function(d) { return d.depth ? null : 'none'; })
            .attr('d', arc)
            .attr('fill-rule', 'evenodd')
            .attr('class', 'sunburst-segment')
            .style('fill', function(d) { return sunburstColorScale(d.account); })
            .on('mouseover', mouseOver)
            .on('click', function(d) {
                window.location = accountUrl.replace('REPLACEME', d.account);
                d3.event.stopPropagation()
            });

        setLabel(root);
        // Add the mouseleave handler to the bounding circle.
        vis.on('mouseleave', mouseLeave);
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
            .on('click', function(d) {
                window.location = accountUrl.replace('REPLACEME', d.account);
                d3.event.stopPropagation()
            });
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

function lineChart(chart) {
    var options = {
        axisX: {
            type: Chartist.AutoScaleAxis,
            scaleMinSpace: 25,
            labelInterpolationFnc: function(value, index) {
                var val = helpers.isNumber(value) ? new Date(value) : value;
                return val.formatWithString(chart.options.dateFormat ? chart.options.dateFormat : "MMM YYYY");
            }
        },
        lineSmooth: Chartist.Interpolation.none()
    };

    defaultOptions.plugins.push(Chartist.plugins.zoom({
        onZoom : function(chart, reset) {
            var dateStart = new Date(chart.options.axisX.highLow.low);
            var dateEnd = new Date(chart.options.axisX.highLow.high);

            var dateStringStart = '' + dateStart.getFullYear() + '-' + (helpers.pad(dateStart.getMonth()+1));
            var dateStringEnd = '' + dateEnd.getFullYear() + '-' + (helpers.pad(dateEnd.getMonth()+1));
            var e = $.Event('keyup');
            e.which = 13;
            $("#filter-time input[type=search]").val(dateStringStart + ' - ' + dateStringEnd).trigger(e);
        }
    }));

    return new Chartist.Line("#" + chart.id, chart.data,
        $.extend({}, defaultOptions, options, chart.options)
    );
}

function barChart(chart) {
    var options = {
        axisX: {
            labelInterpolationFnc: function(value, index) {
                if (chart.data.labels.length <= 25 || index % Math.ceil(chart.data.labels.length / 25) === 0) {
                    var val = helpers.isNumber(value) ? new Date(value) : value;
                    return val.formatWithString(chart.options.dateFormat ? chart.options.dateFormat : "MMM YYYY");
                } else {
                    return null;
                }
            }
        }
    };

    defaultOptions.plugins.push(Chartist.plugins.zoom({
        onZoom : function(chart, reset, x1, x2, y1, y2) {
            console.log(x1, x2, y1, y2);
            var width = parseFloat($(chart.container).find('line.ct-bar:last-child').last().attr('x2'));
            var pxPerBar = width / chart.data.labels.length;
            var dateStart = new Date(chart.data.labels[Math.floor(x1 / pxPerBar)]);
            var dateEnd = new Date(chart.data.labels[Math.floor(x2 / pxPerBar)]);

            var dateStringStart = '' + dateStart.getFullYear() + '-' + (helpers.pad(dateStart.getMonth()+1));
            var dateStringEnd = '' + dateEnd.getFullYear() + '-' + (helpers.pad(dateEnd.getMonth()+1));
            var e = $.Event('keyup');
            e.which = 13;
            $("#filter-time input[type=search]").val(dateStringStart + ' - ' + dateStringEnd).trigger(e);
        }
    }));

    var chart = new Chartist.Bar("#" + chart.id, chart.data,
        $.extend({}, defaultOptions, options, chart.options)
    );

    $(chart.container).on('click', '.ct-bar', function() {
        var date = chart.data.labels[$(event.target).index()];
        var e = $.Event('keyup');
        e.which = 13;
        var formatStr = 'YYYY';
        if (window.interval == 'day')     { formatStr = 'YYYY-MM-DD'; }
        if (window.interval == 'week')    { formatStr = 'YYYY-Www'; }
        if (window.interval == 'month')   { formatStr = 'YYYY-MM'; }
        if (window.interval == 'quarter') { formatStr = 'YYYY-Qq'; }
        $("#filter-time input[type=search]").val(date.formatWithString(formatStr)).trigger(e);
    });

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
            .attr('class', 'ct-chart')
            .attr('id', id)

        labels.append('label')
            .attr('for', id)
            .html(label)

        return div;
    }

    $.each(window.chartData, function(index, chart) {
        switch(chart.type) {
            case 'line':
                chart.id = "line-" + index;
                chart.options = $.extend({}, chart.options);
                chartContainer(chart.id, chart.label);

                window.charts[chart.id] = lineChart(chart);
                break;
            case 'bar':
                chart.id = "bar-" + index;
                chart.options = $.extend({}, chart.options);
                chartContainer(chart.id, chart.label);

                window.charts[chart.id] = barChart(chart);
                break;
            case 'treemap': {
                $.each(window.operating_currencies, function(i, currency) {
                    chart.id = "treemap-" + index + '-' + currency;

                    var div = chartContainer(chart.id, chart.label + ' (' + currency + ')');
                    addInternalNodesAsLeaves(chart.root);
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
        }
    });

    var $labels = $('#chart-labels');

    // Switch between charts
    $labels.find('label').click(function() {
        var chartId = $(this).prop('for');
        $('.charts .ct-chart').addClass('hidden')
        $('.charts .ct-chart#' + chartId).removeClass('hidden');

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
            window.location = this.value;
        });
    }
}
