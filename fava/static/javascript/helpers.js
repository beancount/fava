export function $(expr, con) {
  return (con || document).querySelector(expr);
}

export function $$(expr, con) {
  return Array.from((con || document).querySelectorAll(expr));
}

$.delegate = function delegate(element, type, selector, callback) {
  element.addEventListener(type, (event) => {
    if (event.target.closest(selector)) {
      callback(event);
    }
  });
};

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
