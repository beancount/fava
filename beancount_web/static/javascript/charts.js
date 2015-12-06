$(document).ready(function() {
    $.each(window.chart_data, function(index, chart) {
        chart.id = "chart-" + index;
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
                            return moment(value).format(chart.dateformat ? chart.dateformat : 'MMM D');
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
                            return moment(value).format(chart.dateformat ? chart.dateformat : "MMM 'YY");
                        }
                    }
                };

                new Chartist.Bar("#" + chart.id, chart.data,
                    $.extend({}, defaultOptions, options, chart.options)
                );

                break;
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



