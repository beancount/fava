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
    if (node.balance.length && node.children.length) {
        var copy = $.extend({}, node)
        copy.children = null;
        node.children.push(copy);
        node.balance = null
    }
};

function treeMap() {
    var width, height, kx, ky;
    var x = d3.scale.linear(), y = d3.scale.linear();
    var treemap = d3.layout.treemap();
    var transitionDelay = 200;
    var div, svg, root, current_node, cells, leaves, tooltipText;

    function setSize() {
        width = parseInt(container.style('width'), 10);
        height = Math.min(width / 2.5, 400);
        svg
            .attr('width', width)
            .attr('height', height)
    }

    function chart(div) {
        svg = div.append("svg")
            .attr('class', 'treemap')

        setSize();

        cells = svg.selectAll('g')
            .data(treemap.size([width, height]).nodes(root))
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

    chart.root = function(r) {
        root = r;
        return chart;
    }

    chart.update = function() {
        transitionDelay = 0;
        setSize();
        zoom(current_node);
        transitionDelay = 200;
    }

    function zoom(d) {
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
                    chart.id = "treemap-" + chart.label + '-' + currency;

                    var div = chartContainer(chart.id, chart.label + ' (' + currency + ')');
                    addInternalNodesAsLeaves(chart.root);
                    var tm = treeMap()
                        .value(function(d) { return d.balance[currency] * chart.modifier; })
                        .tooltipText(function(d) { return d.value + ' ' + currency  + '<em>' + d.account + '</em>'; })
                        .root(chart.root)
                    div
                        .call(tm)
                    window.charts[chart.id] = tm;
                })
                break;
            }
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
