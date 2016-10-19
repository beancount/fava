import Clipboard from 'clipboard';

export default function initClipboard() {
  new Clipboard('.status-indicator'); // eslint-disable-line no-new
  new Clipboard('#copy-balances'); // eslint-disable-line no-new
}
