// Notifications
//
// The three events `error`, `info`, and `reload-warning` allow notifications
// with a given message to be shown. The reload-warning automatically
// disappears and can be clicked to trigger the reload.

import { $ } from './helpers';
import e from './events';

e.on('info', (msg) => {
  $('#notifications').insertAdjacentHTML('beforeend', `<li>${msg}</li>`);
});

e.on('reload-warning', (msg) => {
  $('#notifications').insertAdjacentHTML('beforeend', `<li class="warning">${msg}</li>`);
  const warning = $('#notifications').lastChild;
  warning.addEventListener('click', () => {
    warning.remove();
    e.trigger('reload');
  });
  setTimeout(() => {
    warning.remove();
  }, 5000);
});

e.on('error', (msg) => {
  $('#notifications').insertAdjacentHTML('beforeend', `<li class="error">${msg}</li>`);
});

e.on('page-init', () => {
  $.delegate($('#notifications'), 'click', 'li', (event) => {
    event.target.closest('li').remove();
  });
});
