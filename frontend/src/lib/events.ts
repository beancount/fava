/**
 * Execute the callback of the event of given type is fired on something
 * matching selector.
 *
 * @param element - The ancestor element that the listener will be attached to.
 * @param type - The event type to listen to.
 * @param selector - The DOM selector to match.
 * @param callback - The event listener to execute on a match.
 */
export function delegate<K extends keyof HTMLElementEventMap>(
  element: HTMLElement,
  type: K,
  selector: string,
  callback: (e: HTMLElementEventMap[K], c: Element) => void,
): void;
export function delegate<K extends keyof DocumentEventMap>(
  element: Document,
  type: K,
  selector: string,
  callback: (e: DocumentEventMap[K], c: Element) => void,
): void;
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
