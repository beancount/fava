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

    // if (isset("data_account")) {
    //     new Chartist.Line('#chart-account', {
    //         series: [{
    //             name: 'remaining',
    //             data: data_account
    //         }]
    //     }, { // options
    //         axisX: {
    //             type: Chartist.FixedScaleAxis,
    //             divisor: data_account.length > 15 ? 15 : data_account.length,  // no of days
    //             labelInterpolationFnc: function(value) {
    //                 return moment(value).format('MMM D');
    //             }
    //         },
    //         axisY: {
    //             onlyInteger: true,
    //             // low: 0,
    //             position: 'end',
    //             labelInterpolationFnc: function(value) {
    //                 return value.toLocaleString();
    //             }
    //         },
    //         series: {
    //             remaining: {
    //                 // lineSmooth: Chartist.Interpolation.step(),
    //                 // showPoint: true
    //             },
    //         },
    //         height: 240,
    //         width: $('.charts').width(),
    //         chartPadding: { left: 3 }
    //     });
    // }

    // if (isset("data_monthly_totals")) {
        // new Chartist.Bar('#chart-monthly-totals', data_monthly_totals, {
        //     height: 240,
        //     width: $('.charts').width(),
        //     chartPadding: { left: 0, right: 0 },
        //     axisY: {
        //         onlyInteger: true,
        //         referenceValue: 0,
        //         position: 'end',
        //         scaleMinSpace: 15,
        //         labelInterpolationFnc: function(value) {
        //             return value.toLocaleString();
        //         }
        //     },
        //     axisX: {
        //         divisor: data_monthly_totals.length > 15 ? 15 : data_monthly_totals.length,  // no of days
        //         labelInterpolationFnc: function(value, index) {
        //             return moment(value).format("MMM 'YY");
        //         }
        //     }
        // });
    // }

    // Toggle multiple charts
    $('.charts .chart-labels label').click(function() {
        $('.charts .ct-chart').hide();
        $('.charts .ct-chart#' + $(this).prop('for')).show();

        $('.charts .chart-labels label').removeClass('selected');
        $(this).addClass('selected');
    });
    $('.charts .chart-labels label:first-child').click();

    // Toggle chart by clicking on "Hide/Show chart"
    $('.charts input#toggle-chart').click(function() {
        $('.ct-chart, .chart-labels').not('.hidden').toggle($(this).hasClass('hide-charts'));
        $(this).toggleClass('hide-charts');

        var text = $(this).prop('value');
        $(this).prop('value', text === 'Hide chart' ? 'Show chart' : 'Hide chart');

        return false;
    });
});



