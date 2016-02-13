Chartist = require('chartist');
require('chartist-plugin-legend');
require('chartist-plugin-tooltip');
require('./vendor/chartist-plugin-zoom');

require('jquery-treemap/src/jquery-treemap');

require('./helpers');

$(document).ready(function() {
    $('.charts-container').html('');
    window.chartData.charts = {}

    $.each(window.chartData, function(index, chart) {
        chart.id = "chart-" + index;
        chart.options = $.extend({}, chart.options);

        $('.charts-container').append('<div class="ct-chart" id="' + chart.id + '"></div>');
        var divider = $('.chart-labels').children().length > 0 ? " | " : "";
        $('.chart-labels').append(divider + '<label for="' + chart.id + '">' + chart.label + '</label>');

        var defaultOptions = {
            height: 240,
            chartPadding: { left: 3 },
            axisY: {
                onlyInteger: true,
                position: 'end',
                scaleMinSpace: 15,
                labelInterpolationFnc: function(value) {
                    return value;
                },
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

        switch(chart.type) {
            case 'line':
                var options = {
                    axisX: {
                        type: Chartist.AutoScaleAxis,
                        scaleMinSpace: 25,
                        labelInterpolationFnc: function(value, index) {
                            var val = isNumber(value) ? new Date(value) : value;
                            return val.formatWithString(chart.options.dateFormat ? chart.options.dateFormat : "MMM 'YY");
                        }
                    },
                    lineSmooth: Chartist.Interpolation.none()
                };

                defaultOptions.plugins.push(Chartist.plugins.zoom({
                    onZoom : function(chart, reset) {
                        var dateStart = new Date(chart.options.axisX.highLow.low);
                        var dateEnd = new Date(chart.options.axisX.highLow.high);

                        var dateStringStart = '' + dateStart.getFullYear() + '-' + (pad(dateStart.getMonth()+1));
                        var dateStringEnd = '' + dateEnd.getFullYear() + '-' + (pad(dateEnd.getMonth()+1));
                        var e = $.Event('keyup');
                        e.which = 13;
                        $("#filter-time input[type=search]").val(dateStringStart + ' - ' + dateStringEnd).trigger(e);
                    }
                }));

                window.chartData.charts[chart.id] = new Chartist.Line("#" + chart.id, chart.data,
                    $.extend({}, defaultOptions, options, chart.options)
                );
                break;
            case 'bar':
                var options = {
                    axisX: {
                        labelInterpolationFnc: function(value, index) {
                            if (chart.data.labels.length <= 25 || index % Math.ceil(chart.data.labels.length / 25) === 0) {
                                var val = isNumber(value) ? new Date(value) : value;
                                return val.formatWithString(chart.options.dateFormat ? chart.options.dateFormat : "MMM 'YY");
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

                        var dateStringStart = '' + dateStart.getFullYear() + '-' + (pad(dateStart.getMonth()+1));
                        var dateStringEnd = '' + dateEnd.getFullYear() + '-' + (pad(dateEnd.getMonth()+1));
                        var e = $.Event('keyup');
                        e.which = 13;
                        $("#filter-time input[type=search]").val(dateStringStart + ' - ' + dateStringEnd).trigger(e);
                    }
                }));

                window.chartData.charts[chart.id] = new Chartist.Bar("#" + chart.id, chart.data,
                    $.extend({}, defaultOptions, options, chart.options)
                );
                var chart = window.chartData.charts[chart.id];

                $(chart.container).on('click', '.ct-bar', function() {
                    var date = chart.data.labels[$(event.target).index()];
                    var dateString = '' + date.getFullYear() + '-' + (pad(date.getMonth()+1));
                    var e = $.Event('keyup');
                    e.which = 13;
                    $("#filter-time input[type=search]").val(dateString).trigger(e);
                });

                break;
            case 'treemap': {
                var colors = ['#990000', '#113861', '#777', '#1B9900', '#FF8800', '#59922b', '#0544d3', '#6b0392', '#f05b4f', '#dda458', '#eacf7d', '#86797d', '#b2c326', '#6188e2', '#a748ca'].reverse();
                var backupColor = '#949494';
                var colorsMap = {};

                var options =     {
                    backgroundColor: function ($box, node) {
                        var parentName = node.accountName.split(':')[chart.options.treemapColorLevel ? chart.options.treemapColorLevel : 0];
                        if (!(parentName in colorsMap)) { colorsMap[parentName] = colors.pop(); }
                        if (colorsMap[parentName] == undefined) { return backupColor; }
                        return colorsMap[parentName];
                    },
                    smallestFontSize: 6,
                    startingFontSize: 15,
                    centerLabelVertically: true,
                    itemMargin: 3,
                    mouseenter: function (node, event) {
                        $(event.target).append('<div class="treetable-popover"></div>');
                        var $popover = $('.treetable-popover');
                        $popover.html('<dl><dt>Account:</dt><dd>' + node.accountName + '</dd><dt>Balance:</dt><dd><code>' + node.balance + '</code></dd></dl>').hide().fadeIn(200);

                        var windowWidth = $(window.window).width();
                        var left = node.bounds.width / 2 - ($popover.width() / 2) - 10,
                        left = (left + $popover.width() > windowWidth) ? (windowWidth - $popover.width()) : left;
                        $popover.css({
                            left: left,
                            top:  node.bounds.height / 2 - $popover.height() - 30
                        });
                    },
                    mouseleave: function (node, event) {
                        $('.treetable-popover').remove();
                    },
                    ready: function () {
                        if (chart.data.length == 0) {
                            $('div#' + chart.id).addClass('chart-no-data').html('<div>Chart is empty.</div>');
                        }
                    }
                };

                $('div#' + chart.id).css('margin', '8px 0').append('<div id="' + chart.id + '-container" style="height: 230px; width: ' + $('div#' + chart.id).parent().width() + 'px;"></div>');
                $('div#' + chart.id + '-container').treemap(chart.data,
                    $.extend({}, options, chart.options)
                );
                break;
            }
            default:
                console.error('Chart-Type "' + chart.type + '" unknown.');
        }
    });

    // Toggle multiple charts
    $('.charts .chart-labels label').click(function() {
        var chartId = $(this).prop('for');
        $('.charts .ct-chart').addClass('hidden')
        $('.charts .ct-chart#' + chartId).removeClass('hidden');

        $('.charts .chart-labels label').removeClass('selected');
        $(this).addClass('selected');

        if (window.chartData.charts[chartId] !== undefined) {
            window.chartData.charts[chartId].update();
        }
    });
    $('.charts .chart-labels label:first-child').click();

    // Toggle chart by clicking on "Hide/Show chart"
    $('.charts input#toggle-chart').click(function() {
        $('.charts-container, .chart-labels').toggle($(this).hasClass('hide-charts'));
        $(this).toggleClass('hide-charts');

        var text = $(this).prop('value');
        $(this).prop('value', text === 'Hide charts' ? 'Show charts' : 'Hide charts');

        return false;
    });
});



