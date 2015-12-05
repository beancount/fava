function isset(object){
    return (object in window);  // only works in a browser
}

$.expr[":"].contains = $.expr.createPseudo(function(arg) {
    return function( elem ) {
        return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
    };
});

//  Checks that string starts with the specific string
if (typeof String.prototype.startsWith != 'function') {
    String.prototype.startsWith = function (str) {
        return this.slice(0, str.length) == str;
    };
}

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
            // showPoint: true
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

    function toggle_journal_types() {
        $('.table-filter input[type="checkbox"]').each(function() {
            var type = $(this).prop('id').substring(7);
            $('table.entry-table tr.' + type).toggle($(this).prop('checked'));
            $('table.entry-table tr.leg-' + type).toggle($(this).prop('checked'));
            $('table.entry-table tr.leg-' + type).toggleClass('hidden', !$(this).prop('checked'));
        });
    }

    // Toggle positions with checkboxes
    $('.table-filter input[type="checkbox"]').change(function() {
        toggle_journal_types();
    });
    toggle_journal_types();

    // Toggle legs by clicking on transaction/padding row
    $('table.entry-table tr.transaction td, table.entry-table tr.padding td').click(function() {
        $.each($(this).parents('tr').prop('class').split(' '), function(index, clazz) {
            if (clazz.startsWith('journal-entry-')) {
                $('table.entry-table tr.leg.' + clazz).toggle();
                $('table.entry-table tr.leg.' + clazz).toggleClass('hidden');
            }
        });
    });

    // Toggle all legs by clicking on "Hide/Show legs"
    $('.table-filter input#toggle-legs').click(function() {
        $('table.entry-table tr.leg').not('.hidden').toggle($(this).hasClass('hide-legs'));
        $(this).toggleClass('hide-legs');

        var text = $(this).prop('value');
        $(this).prop('value', text === 'Hide legs' ? 'Show legs' : 'Hide legs');

        return false;
    });

    // Toggle chart by clicking on "Hide/Show chart"
    $('.charts input#toggle-chart').click(function() {
        $('.ct-chart, .chart-labels').not('.hidden').toggle($(this).hasClass('hide-charts'));
        $(this).toggleClass('hide-charts');

        var text = $(this).prop('value');
        $(this).prop('value', text === 'Hide chart' ? 'Show chart' : 'Hide chart');

        return false;
    });
});



