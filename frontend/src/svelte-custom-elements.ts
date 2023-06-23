/**
 * A custom element that will render a Svelte component.
 */

import type { SvelteComponent } from "svelte";

import ChartSwitcher from "./charts/ChartSwitcher.svelte";
import SliceEditor from "./editor/SliceEditor.svelte";

const components = new Map<
  string,
  typeof SvelteComponent<Record<string, unknown>>
>([
  ["charts", ChartSwitcher],
  ["slice-editor", SliceEditor],
]);

/**
 * A custom element that represents a Svelte component.
 *
 * The tag should have a `type` attribute with one
 * of the valid values in the Map above.
 */
export class SvelteCustomElement extends HTMLElement {
  component?: SvelteComponent<Record<string, unknown>>;

  connectedCallback(): void {
    if (this.component) {
      return;
    }
    const type = this.getAttribute("type");
    if (!type) {
      throw new Error("Component is missing type");
    }
    const Cls = components.get(type);
    if (!Cls) {
      throw new Error("Invalid component");
    }
    const props: Record<string, unknown> = {};
    const script = this.querySelector("script");
    if (script && script.type === "application/json") {
      const data: unknown = JSON.parse(script.innerHTML);
      if (data instanceof Object) {
        Object.assign(props, data);
      }
    }
    this.component = new Cls({ target: this, props });
  }

  disconnectedCallback(): void {
    try {
      this.component?.$destroy();
      this.component = undefined;
    } catch (e) {
      // pass
    }
  }
}
