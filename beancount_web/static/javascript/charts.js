$(document).ready(function() {
    $('.charts-container').html('');

    $.each(window.chartData, function(index, chart) {
        chart.id = "chart-" + index;
        chart.options = $.extend({}, chart.options);

        $('.charts-container').append('<div class="ct-chart" id="' + chart.id + '"></div>');
        var divider = $('.chart-labels').children().length > 0 ? " | " : "";
        $('.chart-labels').append(divider + '<label for="' + chart.id + '">' + chart.label + '</label>');

        var defaultOptions = {
            height: 240,
            width: $('.charts').width(),
            chartPadding: { left: 3 },
            axisY: {
                onlyInteger: true,
                position: 'end',
                scaleMinSpace: 15,
                labelInterpolationFnc: function(value) {
                    return value.toLocaleString();
                },
                referenceValue: 0,
            },
            plugins: [
                Chartist.plugins.legend()
            ]
        };

        switch(chart.type) {
            case 'line':
                var options = {
                    axisX: {
                        type: Chartist.FixedScaleAxis,
                        divisor: chart.data.series[0].data.length > 15 ? 15 : chart.data.series[0].data.length,  // no of days
                        labelInterpolationFnc: function(value) {
                            return moment(value).format(chart.options.dateformat ? chart.options.dateformat : "MMM 'YY");
                        }
                    },
                    lineSmooth: Chartist.Interpolation.none()
                };

                new Chartist.Line("#" + chart.id, chart.data,
                    $.extend({}, defaultOptions, options, chart.options)
                );
                break;
            case 'bar':
                var options = {
                    axisX: {
                        labelInterpolationFnc: function(value, index) {
                            return moment(value).format(chart.options.dateformat ? chart.options.dateformat : "MMM 'YY");
                        }
                    }
                };

                new Chartist.Bar("#" + chart.id, chart.data,
                    $.extend({}, defaultOptions, options, chart.options)
                );

                break;
            case 'treemap': {
                var colors = ['#990000', '#113861', '#777', '#1B9900', '#FF8800', '#59922b', '#0544d3', '#6b0392', '#f05b4f', '#dda458', '#eacf7d', '#86797d', '#b2c326', '#6188e2', '#a748ca'].reverse();
                var colorsMap = {};

                var options =     {
                    backgroundColor: function ($box, node) {
                        var parentName = node.accountName.split(':')[chart.options.treemapColorLevel ? chart.options.treemapColorLevel : 0];
                        if (!(parentName in colorsMap)) { colorsMap[parentName] = colors.pop(); }
                        return colorsMap[parentName];
                    },
                    smallestFontSize: 6,
                    startingFontSize: 15,
                    centerLabelVertically: true,
                    itemMargin: 3,
                    mouseenter: function (node, event) {
                        $('.charts-container').append('<div id="treetable-popover"></div>');
                        $('#treetable-popover').html('<dl><dt>Account:</dt><dd>' + node.accountName + '</dd><dt>Balance:</dt><dd><pre>' + node.balance + '</pre></dd></dl>').hide().fadeIn(200);
                    },
                    mousemove: function (node, event) {
                        var windowWidth = $(window.window).width();
                        var popover = $('#treetable-popover');
                        var left = event.pageX + popover.width() + 45 > windowWidth ? windowWidth - $('#treetable-popover').width() - 45 : event.pageX;
                        $('#treetable-popover').css({
                           left:  left,
                           top:   event.pageY
                        });
                    },
                    mouseleave: function (node, event) {
                        $('#treetable-popover').remove();
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
        $('.charts .ct-chart').addClass('hidden')
        $('.charts .ct-chart#' + $(this).prop('for')).removeClass('hidden');

        $('.charts .chart-labels label').removeClass('selected');
        $(this).addClass('selected');
    });
    $('.charts .chart-labels label:first-child').click();

    // Toggle chart by clicking on "Hide/Show chart"
    $('.charts input#toggle-chart').click(function() {
        $('.charts-container, .chart-labels').toggle($(this).hasClass('hide-charts'));
        $(this).toggleClass('hide-charts');

        var text = $(this).prop('value');
        $(this).prop('value', text === 'Hide chart' ? 'Show chart' : 'Hide chart');

        return false;
    });
});



