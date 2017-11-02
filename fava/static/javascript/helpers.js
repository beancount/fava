// Select a single element.
export function $(expr, con = document) {
  return con.querySelector(expr);
}

// Select multiple elements (and convert NodeList to Array).
export function $$(expr, con = document) {
  return Array.from(con.querySelectorAll(expr));
}

// Execute the callback of the event of given type is fired on something
// matching selector.
$.delegate = function delegate(element, type, selector, callback) {
  element.addEventListener(type, (event) => {
    if (event.target.closest(selector)) {
      callback(event);
    }
  });
};

// Create a new object that has all properties of the arguments.
$.extend = function extend(...args) {
  const newObject = {};
  args.forEach((object) => {
    Object.keys(object).forEach((i) => {
      if ({}.hasOwnProperty.call(object, i)) {
        newObject[i] = object[i];
      }
    });
  });
  return newObject;
};

// Bind an event to element, only run the callback once.
$.once = function once(element, event, callback) {
  function runOnce(...args) {
    element.removeEventListener(event, runOnce);
    callback.apply(element, args);
  }

  element.addEventListener(event, runOnce);
};

$.ready = function ready() {
  return new Promise((resolve) => {
    if (document.readyState !== 'loading') {
      resolve();
    } else {
      document.addEventListener('DOMContentLoaded', resolve());
    }
  });
};

$.fetch = function fetch(input, init) {
  let def = {
    credentials: 'same-origin',
  };
  if (init) {
    def = $.extend(def, init);
  }
  return window.fetch(input, def);
};

// Fuzzy match a pattern against a string.
//
// Returns true if all characters of `pattern` can be found in order in
// `string`. For lowercase characters in `pattern` match both lower and upper
// case, for uppercase only an exact match counts.
export function fuzzytest(pattern, string) {
  let pindex = 0;
  for (let index = 0; index < string.length; index += 1) {
    const char = string[index];
    const search = pattern[pindex];
    if (char === search || char.toLowerCase() === search) {
      pindex += 1;
    }
  }
  return pindex === pattern.length;
}

// Wrap fuzzy matched characters.
//
// Wrap all occurences of characters of `pattern` (in order) in `string` in
// <span> tags.
export function fuzzywrap(pattern, string) {
  let pindex = 0;
  const result = [];
  for (let index = 0; index < string.length; index += 1) {
    const char = string[index];
    const search = pattern[pindex];
    if (char === search || char.toLowerCase() === search) {
      result.push(`<span>${char}</span>`);
      pindex += 1;
    } else {
      result.push(char);
    }
  }
  return result.join('');
}

// Handles JSON content for a Promise returned by fetch, also handling an HTTP
// error status.
export function handleJSON(response) {
  if (!response.ok) {
    return Promise.reject(response.statusText);
  }
  return response.json()
    .then((data) => {
      if (!data.success) {
        return Promise.reject(data.error);
      }
      return data;
    });
}
