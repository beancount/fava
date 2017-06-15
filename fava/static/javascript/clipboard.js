import Clipboard from 'clipboard';

import e from './events';

e.on('page-loaded', () => {
  new Clipboard('.status-indicator'); // eslint-disable-line no-new
  new Clipboard('#copy-balances'); // eslint-disable-line no-new
});
