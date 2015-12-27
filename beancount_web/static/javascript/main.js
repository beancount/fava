$(document).ready(function() {
    $("table.sortable").stupidtable();

    $('.filter input').keyup(function() {
        var $this = $(this);
        var value = $this.val();
        $(this).parents('.filter').find('li.suggestion').toggle(value == '');
        $(this).parents('.filter').find("li[data-filter*='" + value.toLowerCase() + "']").show();
    });

    $('.filter#filter-time input').keyup(function(e) {
        var $this = $(this);
        var code = e.which;
        if (code == 13) {
            e.preventDefault();
            window.location.href = location.pathname + ($.query.set('time', $this.val()));
        }
    });

    // Tree-expanding

    // This fixes if there is a tree-balance, no balance and the row is not a parent.
    // Without this code the tree-balance would not be shown.
    $('table.tree-table tbody tr td:not(:first)').each(function(index, td) {
        if ($(td).find('span.balance').length == 0) {
            $(td).addClass('tree-balance-show');
        }
    });

    function getLevel(tableRow) {
        if ($(tableRow).length == 0) { return 0; }
        var rowLevel = parseInt($(tableRow).attr('data-level'));
        return rowLevel;
    }

    var level = 1;
    $('table.tree-table tr').each(function() {
        var nextLevel = getLevel($(this).next());
        if (nextLevel <= level) { $(this).children().first().addClass('leaf'); }
        level = nextLevel;
    });

    $('table.tree-table tr td:first-child:not(.leaf) a.account').each(function() {
        $(this).append('<span class="expander"></span>');
    });

    $('table.tree-table span.expander').click(function() {
        var row = $(this).parents('tr');
        var level = getLevel(row);
        var hide = !$(this).hasClass('toggled');
        $(this).toggleClass('toggled');

        row.toggleClass('hides', hide);
        row = row.next();
        while (row.length > 0 && getLevel(row) > level) {
            row.toggleClass('hidden', hide);
            row.find('span.expander').removeClass('toggled');
            row = row.next();
        }

        return false;
    });

    // Keyboard shortcuts

    // Filtering:
    $("body").click(function(){
      $("ul.topmenu li").removeClass("selected");
    });

    $("ul.topmenu li").click(function(e){
      e.stopPropagation();
    });

    $('ul.topmenu input[type=search]').keyup(function(e) {
        if (e.which == 27) {
            $(this).blur();
            $(this).parents('li').removeClass("selected");
        }
    });

    // Jumping through charts
    if ($('.chart-labels').length) {
        Mousetrap.bind({
            'shift+c': function() { $('#toggle-chart').click(); },
            'c':       function() {
                var next = $('.chart-labels label.selected').next();
                $('.chart-labels label').removeClass('selected');
                if (next.length) { next.click(); }
                else             { $('.chart-labels label:first-child').click(); }
            },

        }, 'keyup');
    }

    // Options in transaction pages:
    if ($('.table-filter').length) {
        Mousetrap.bind({
            'l':   function() { $('#toggle-legs').click(); },
            's l': function() { $('#toggle-legs').click(); },
            'm':   function() { $('#toggle-metadata').click(); },
            's m': function() { $('#toggle-metadata').click(); },
            's o': function() { $('input#filter-open').click(); },
            's c': function() { $('input#filter-close').click(); },
            's t': function() { $('input#filter-transaction').click(); },
            's b': function() { $('input#filter-balance').click(); },
            's n': function() { $('input#filter-note').click(); },
            's d': function() { $('input#filter-document').click(); },
            's p': function() { $('input#filter-pad').click(); },
            's shift+p': function() { $('input#filter-padding').click(); }
        }, 'keyup');
    }
});



