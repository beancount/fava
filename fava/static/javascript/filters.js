module.exports.initFilters = function() {
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

    $("body").click(function(){
        $("ul.topmenu li").removeClass("opened");
    });

    $("ul.topmenu li").click(function(e){
        e.stopPropagation();
    });

    $('ul.topmenu input[type=search]').keyup(function(e) {
        if (e.which == 27) {
            $(this).blur();
            $(this).parents('li').removeClass("opened");
        }
    });
};
