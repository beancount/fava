// Minimal event handler
class Events {
  constructor() {
    this.events = {};
  }

  on(event, callback) {
    this.events[event] = this.events[event] || [];
    this.events[event].push(callback);
  }

  trigger(event, ...args) {
    if (!this.events[event]) {
      return;
    }
    this.events[event].forEach((callback) => {
      callback(args);
    });
  }
}

const e = new Events();
export default e;
