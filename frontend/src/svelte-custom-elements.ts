/**
 * A custom element that will render a Svelte component.
 */

import type { SvelteComponentTyped } from "svelte";

import ChartSwitcher from "./charts/ChartSwitcher.svelte";

const components = new Map<
  string,
  typeof SvelteComponentTyped<{ data?: unknown }>
>([["charts", ChartSwitcher]]);

/**
 * A custom element that represents a Svelte component.
 *
 * The tag should have a `type` attribute with one
 * of the valid values in the Map above.
 */
export class SvelteCustomElement extends HTMLElement {
  component?: SvelteComponentTyped<{ data?: unknown }>;

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
    const props: { data?: unknown } = {};
    const script = this.querySelector("script");
    if (script && script.type === "application/json") {
      props.data = JSON.parse(script.innerHTML);
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
