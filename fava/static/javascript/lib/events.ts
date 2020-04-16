/**
 * Minimal event handler
 */
export class Events<T = string> {
  private events: Map<T, (() => void)[]>;

  constructor() {
    this.events = new Map();
  }

  /**
   * Register an event listener.
   */
  on(event: T, callback: () => void): void {
    const events = this.events.get(event) ?? [];
    this.events.set(event, [...events, callback]);
  }

  /**
   * Register an event listener that will only be executed once.
   */
  once(event: T, callback: () => void): void {
    const runOnce = (): void => {
      this.remove(event, runOnce);
      callback();
    };

    this.on(event, runOnce);
  }

  /**
   * Remove an event listener.
   */
  remove(event: T, callback: () => void): void {
    const events = this.events.get(event);
    if (events) {
      this.events.set(
        event,
        events.filter((c) => c !== callback)
      );
    }
  }

  /**
   * Trigger all listeners for an event.
   */
  trigger(event: T): void {
    const events = this.events.get(event);
    events?.forEach((callback) => {
      callback();
    });
  }
}
