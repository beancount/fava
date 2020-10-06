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

/**
 * Execute the callback of the event of given type is fired on something
 * matching selector.
 *
 * @param element - The ancestor element that the listener will be attached to.
 * @param type - The event type to listen to.
 * @param selector - The DOM selector to match.
 * @param callback - The event listener to execute on a match.
 */
export function delegate<T extends Event, C extends Element>(
  element: Element | Document,
  type: string,
  selector: string,
  callback: (e: T, c: C) => void
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
        callback(event as T, closest as C);
      }
    }
  });
}

/**
 * Bind an event to element, only run the callback once.
 * @param element - The element to attach the listener to.
 * @param event - The event type.
 * @param callback - The event listener.
 */
export function once(
  element: EventTarget,
  event: string,
  callback: (ev: Event) => void
): void {
  function runOnce(ev: Event): void {
    element.removeEventListener(event, runOnce);
    callback.apply(element, [ev]);
  }

  element.addEventListener(event, runOnce);
}
