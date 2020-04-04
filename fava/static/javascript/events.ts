type EventHandler = () => void;

/**
 * Minimal event handler
 */
class Events {
  events: Record<string, EventHandler[]>;

  constructor() {
    this.events = {};
  }

  on(event: string, callback: EventHandler): void {
    this.events[event] = this.events[event] || [];
    this.events[event].push(callback);
  }

  once(event: string, callback: EventHandler): void {
    const runOnce = (): void => {
      this.remove(event, runOnce);
      callback();
    };

    this.on(event, runOnce);
  }

  remove(event: string, callback: EventHandler): void {
    if (!this.events[event].length) {
      return;
    }
    this.events[event] = this.events[event].filter(c => c !== callback);
  }

  trigger(event: string): void {
    if (!this.events[event]) {
      return;
    }
    this.events[event].forEach(callback => {
      callback();
    });
  }
}

// This global event handler is used by separate parts of the UI to
// communicate.
const e = new Events();
export default e;
