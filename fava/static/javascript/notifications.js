// Notifications
//
// The three events `error`, `info`, and `reload-warning` allow notifications
// with a given message to be shown. The reload-warning can be clicked to
// trigger the reload.

import { $ } from './helpers';
import e from './events';

// Show a notification containing the given `msg` text and having class `cls`.
// The notification is automatically removed after 5 seconds and on click
// `callback` is called.
function showNotification(msg, cls, callback) {
  const notification = document.createElement('li');
  if (cls) {
    notification.classList.add(cls);
  }
  notification.appendChild(document.createTextNode(msg));
  $('#notifications').append(notification);
  notification.addEventListener('click', () => {
    notification.remove();
    if (callback) {
      callback();
    }
  });
  setTimeout(() => {
    notification.remove();
  }, 5000);
}

e.on('info', msg => {
  showNotification(msg);
});

e.on('reload-warning', msg => {
  showNotification(msg, 'warning', () => {
    e.trigger('reload');
  });
});

e.on('error', msg => {
  showNotification(msg, 'error');
});

e.on('page-init', () => {
  $.delegate($('#notifications'), 'click', 'li', event => {
    event.target.closest('li').remove();
  });
});
