function isset(object){
    return (object in window);  // only works in a browser
}

$.expr[":"].contains = $.expr.createPseudo(function(arg) {
    return function( elem ) {
        return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
    };
});

$(document).ready(function() {
    $('.filter input').keyup(function() {
        var value = $(this).val();

        $(this).parents('.filter').find('li:not(:contains(' + value + '))').hide();
        $(this).parents('.filter').find('li:contains(' + value + ')').show();
    });

    if (isset("data_account")) {
      new Chartist.Line('#chart-account', {
        series: [{
          name: 'remaining',
          data: data_account
        }]
      }, { // options
        axisX: {
          type: Chartist.FixedScaleAxis,
          divisor: data_account.length > 15 ? 15 : data_account.length,  // no of days
          labelInterpolationFnc: function(value) {
            return moment(value).format('MMM D');
          }
        },
        axisY: {
          onlyInteger: true,
          // low: 0,
          position: 'end',
        },
        series: {
          remaining: {
            lineSmooth: Chartist.Interpolation.step(),
            showPoint: false
          },
        },
        height: 240,
        chartPadding: { left: 0, right: 0 }
      });
    }

    if (isset("data_monthly_totals")) {
      new Chartist.Bar('#chart-monthly-totals', data_monthly_totals, {
        // high: 10,
        // low: -10,
        height: 240,
        chartPadding: { left: 0, right: 0 },
        axisY: {
             onlyInteger: true,
             referenceValue: 0,
             position: 'end',
             scaleMinSpace: 15
           },
        axisX: {
          // type: Chartist.FixedScaleAxis,
          divisor: data_monthly_totals.length > 15 ? 15 : data_monthly_totals.length,  // no of days
          labelInterpolationFnc: function(value, index) {
            return moment(value).format("MMM 'YY");
          }
        }
      });

    }
});



