// Minimal event handler
class Events {
  constructor() {
    this.events = {};
  }

  on(event, callback) {
    this.events[event] = this.events[event] || [];
    this.events[event].push(callback);
  }

  once(event, callback) {
    const runOnce = (...args) => {
      this.remove(event, runOnce);
      callback(...args);
    };

    this.on(event, runOnce);
  }

  remove(event, callback) {
    if (!this.events[event].length) return;
    this.events[event] = this.events[event].filter(c => c !== callback);
  }

  trigger(event, ...args) {
    if (!this.events[event]) {
      return;
    }
    this.events[event].forEach(callback => {
      callback(...args);
    });
  }
}

// This global event handler is used by separate parts of the UI to
// communicate.
const e = new Events();
export default e;
