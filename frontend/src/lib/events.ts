/**
 * Minimal event handler
 */
export class Events<T = string> {
  private events: Map<T, (() => void)[]>;

  constructor() {
    this.events = new Map<T, (() => void)[]>();
  }

  /**
   * Register an event listener.
   *
   * @returns A function to remove the event listener.
   */
  on(event: T, callback: () => void): () => void {
    const events = this.events.get(event) ?? [];
    this.events.set(event, [...events, callback]);

    return () => {
      this.remove(event, callback);
    };
  }

  /**
   * Register an event listener that will only be executed once.
   */
  once(event: T, callback: () => void): void {
    const runOnce = () => {
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
        events.filter((c) => c !== callback),
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

/**
 * Execute the callback of the event of given type is fired on something
 * matching selector.
 *
 * @param element - The ancestor element that the listener will be attached to.
 * @param type - The event type to listen to.
 * @param selector - The DOM selector to match.
 * @param callback - The event listener to execute on a match.
 */
export function delegate(
  element: HTMLElement | Document,
  type: string,
  selector: string,
  callback: (e: Event, c: Element) => void,
): void {
  element.addEventListener(type, (event) => {
    let { target } = event;
    if (!(target instanceof Node)) {
      return;
    }
    if (!(target instanceof Element)) {
      target = target.parentNode;
    }
    if (target instanceof Element) {
      const closest = target.closest(selector);
      if (closest) {
        callback(event, closest);
      }
    }
  });
}
