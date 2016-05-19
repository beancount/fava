require('awesomplete');

module.exports.initFilters = function() {
    $('#filter-form input').on('input', function() {
        var isEmpty = !$(this).val();
        $(this).parents('li').find('button').toggle(!isEmpty);
        $(this).toggleClass('empty', isEmpty);
    });

    $('#filter-form input[type="text"]').each(function() {
        var options = {
            minChars: 0,
            maxItems: 30,
        };
        if ($(this).attr('name') == 'tag' || $(this).attr('name') == 'payee') {
            options = $.extend(options, {
                filter: function(text, input) {
                    return Awesomplete.FILTER_CONTAINS(text, input.match(/[^,]*$/)[0]);
                },
                replace: function(text) {
                    var before = this.input.value.match(/^.+,\s*|/)[0];
                    this.input.value = before + text + ", ";
                },
            });
        };

        var completer = new Awesomplete(this, options);

        var isEmpty = !$(this).val();
        $(this).parents('li').find('button').toggle(!isEmpty);
        $(this).toggleClass('empty', isEmpty);

        $(this).focus(function() {
            completer.evaluate();
        });
    });

    $('#filter-form button').click(function() {
        $(this).parents('li').find('input').val('');
        $('#filter-form').submit();
    });
};
