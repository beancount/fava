import e from './events';
import { $, fuzzytest, fuzzywrap, handleJSON } from './helpers';

const accountCompletionCache = {};

// An autocompletion dropdown list.
//
// On initialization, adds a list to the DOM, which is filled with suggestions
// as provided by `.suggestions()` when `.show(input)` is called. On changes to
// the value of the input, the list of suggestions is filtered according to
// `.filter(suggestions)`.
class CompletionList {
  // Create and append list to DOM, add event listener to list and create input
  // listeners.
  constructor() {
    const ul = document.createElement('ul');
    document.body.appendChild(ul);
    ul.classList.add('autocomplete');
    this.ul = ul;

    // Clicking on a suggestion selects it.
    ul.addEventListener('mousedown', (event) => {
      if (event.target !== ul && event.button === 0) {
        event.preventDefault();
        this.select(event.target.closest('li'));
        this.close();
      }
    });

    // The events that the active input will listen to.
    this.events = {
      blur: this.close.bind(this),
      input: this.evaluate.bind(this),
      keydown: (event) => {
        if (event.keyCode === 13 && this.index > -1) { // ENTER
          event.preventDefault();
          this.select(ul.children[this.index]);
        } else if (event.keyCode === 27) { // ESC
          this.close();
        } else if (event.keyCode === 38) { // UP
          event.preventDefault();
          this.highlight(this.index === 0 ? ul.children.length - 1 : this.index - 1);
        } else if (event.keyCode === 40) { // DOWN
          event.preventDefault();
          this.highlight(this.index === ul.children.length - 1 ? 0 : this.index + 1);
        }
      },
    };
  }

  // Show the completion list below the given <input> element if the input has
  // a 'list' attribute.
  show(input) {
    this.list = input.getAttribute('list');
    if (!this.list) { return; }

    this.input = input;
    input.setAttribute('autocomplete', 'off');

    input.addEventListener('input', this.events.input);
    input.addEventListener('keydown', this.events.keydown);
    input.addEventListener('blur', this.events.blur);

    this.evaluate();
  }

  // Close, i.e., hide and unbind events.
  close() {
    this.ul.innerHTML = '';
    this.input.removeEventListener('input', this.events.input);
    this.input.removeEventListener('keydown', this.events.keydown);
    this.input.removeEventListener('blur', this.events.blur);
  }

  // Highlight the element at an index.
  highlight(index) {
    const { children } = this.ul;
    if (children.length === 0) {
      this.index = -1;
      return;
    }

    if (children[this.index]) {
      children[this.index].classList.remove('selected');
    }

    const item = children[index];
    item.classList.add('selected');
    this.index = index;
  }

  // Position list and fill with suggestions.
  evaluate() {
    this.ul.innerHTML = '';
    this.suggestions()
      .then((allSuggestions) => {
        this.filter(allSuggestions)
          .forEach((suggestion) => {
            const li = document.createElement('li');
            li.innerHTML = suggestion.innerHTML;
            li.setAttribute('value', suggestion.value);
            this.ul.appendChild(li);
          });
        this.highlight(0);
        this.position();
      });
  }

  // Position the list.
  position() {
    const absolutePosition = this.input.closest('article');
    const coords = this.input.getBoundingClientRect();
    this.ul.style.position = absolutePosition ? 'absolute' : 'fixed';
    this.ul.style.top = `${Math.ceil(coords.top + coords.height) + (absolutePosition ? window.pageYOffset : 0)}px`;
    this.ul.style.left = `${Math.floor(Math.min(coords.left, document.body.clientWidth - this.ul.offsetWidth))}px`;
  }

  // Filter suggestions.
  //
  // Given an array of suggestions, which may be numbers or strings, return a
  // list of {value, innerHTML} for matching suggestions.
  filter(suggestions) {
    let { value } = this.input;
    if (this.list === 'tags') {
      value = value.match(/[^,]*$/)[0].trim();
    }
    return suggestions
      .map(suggestion => String(suggestion))
      .filter(suggestion => fuzzytest(value, suggestion))
      .slice(0, 30)
      .map(suggestion => ({
        value: suggestion,
        innerHTML: fuzzywrap(value, suggestion),
      }));
  }

  // Return a promise that yields the suggestions.
  suggestions() {
    if (this.list === 'accounts' && this.input.closest('.entry-form')) {
      const payee = $('input[name=payee]', this.input.closest('.entry-form')).value.trim();
      if (payee) {
        if (accountCompletionCache[payee]) {
          return new Promise((resolve) => { resolve(accountCompletionCache[payee]); });
        }
        return $.fetch(`${window.favaAPI.baseURL}api/payee-accounts/?payee=${payee}`)
          .then(handleJSON)
          .then(data => data.payload)
          .then((suggestions) => {
            accountCompletionCache[payee] = suggestions;
            return suggestions;
          });
      }
    }
    if (this.list === 'tags') {
      return new Promise((resolve) => { resolve(window.favaAPI[this.list].map(tag => `#${tag}`)); });
    }
    return new Promise((resolve) => { resolve(window.favaAPI[this.list]); });
  }

  // Set the value of the input to the selected value.
  select(li) {
    const value = li.getAttribute('value');
    if (this.list === 'tags') {
      const before = this.input.value.match(/^.+,\s*|/)[0];
      this.input.value = `${before}${value}, `;
    } else {
      this.input.value = value;
    }
    this.input.dispatchEvent(new Event('autocomplete-select'));
    this.close();
  }
}

e.on('page-init', () => {
  const completer = new CompletionList();

  $.delegate(document, 'focusin', 'input', (event) => {
    completer.show(event.target);
  });
});
