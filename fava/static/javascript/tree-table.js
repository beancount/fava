module.exports.initTreeTable = function() {
  $('ol.tree-table span.has-children').click(function(e) {
    var row = $(this).parents('li').first();
    if (e.shiftKey === true) {
      row.find('li').toggleClass('toggled', !row.hasClass('toggled'));
    }
    row.toggleClass('toggled');
    row.parents('ol').find('a.expand-all')
      .toggleClass('hidden', row.parents('ol').find('li.toggled'));
  });

  $('ol.tree-table').on('click', 'a.expand-all', function(e) {
    e.preventDefault();
    var $this = $(e.target);
    $this.parents('ol').find('li.toggled').removeClass('toggled');
    $this.addClass('hidden');
  });
}
