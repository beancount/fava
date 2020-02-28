/**
 * Minimal event handler
 */
class Events {
  events: Record<string, Function[]>;

  constructor() {
    this.events = {};
  }

  on(event: string, callback: Function): void {
    this.events[event] = this.events[event] || [];
    this.events[event].push(callback);
  }

  once(event: string, callback: Function): void {
    const runOnce = (arg: unknown): void => {
      this.remove(event, runOnce);
      callback(arg);
    };

    this.on(event, runOnce);
  }

  remove(event: string, callback: Function): void {
    if (!this.events[event].length) {
      return;
    }
    this.events[event] = this.events[event].filter(c => c !== callback);
  }

  trigger(event: string, arg?: unknown): void {
    if (!this.events[event]) {
      return;
    }
    this.events[event].forEach(callback => {
      callback(arg);
    });
  }
}

// This global event handler is used by separate parts of the UI to
// communicate.
const e = new Events();
export default e;
