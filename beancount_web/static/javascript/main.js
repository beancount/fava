$(document).ready(function() {
    $('aside').css('top', $('header').offset().top + $('header').outerHeight() + 'px');

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
            var value = $this.val();
            window.location.href = $this.attr('data-url') + htmlEncode(value);
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

        var rowLevel = -1;

        $($(tableRow).prop('class').split(' ')).each(function(index, clazz) {
            if (clazz.startsWith('row-level-')) {
                rowLevel = parseInt(clazz.substring(10));
            }
        });

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
            // console.log('row', row, hide, row.prop('class'));
            // row.children().first().toggleClass('hide', hide);
            row.find('span.expander').removeClass('toggled');
            row = row.next();
        }

        return false;
    });
});



