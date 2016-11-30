import Awesomplete from 'awesomplete';

import { $, $$ } from './helpers';

export default function initTransactionForm() {
  const payeeInput = $('#transactions-form input[name="payee"]');
  let options = {
    autoFirst: true,
    minChars: 0,
    maxItems: 30,
    filter(text, input) {
      return Awesomplete.FILTER_CONTAINS(text, input.match(/[^,]*$/)[0]); // eslint-disable-line new-cap, max-len
    }
  };
  const completer = new Awesomplete(payeeInput, options);

  payeeInput.addEventListener('focus', () => {
    completer.evaluate();
  });

  // payeeInput.addEventListener('awesomplete-selectcomplete', () => {
  //   $('#transactions-form').dispatchEvent(new Event('submit'));
  // });
}
