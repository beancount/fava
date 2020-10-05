/**
 * A custom element that will render a Svelte component.
 */

import { SvelteComponent } from "svelte";

import Editor from "./editor/Editor.svelte";
import Import from "./import/Import.svelte";
import ChartSwitcher from "./charts/ChartSwitcher.svelte";
import Documents from "./documents/Documents.svelte";
import Query from "./query/Query.svelte";
import AccountSelector from "./sidebar/AccountSelector.svelte";

const components = new Map([
  ["charts", ChartSwitcher],
  ["documents", Documents],
  ["editor", Editor],
  ["import", Import],
  ["query", Query],
  ["account-selector", AccountSelector],
]);

/**
 * A custom element that represents a Svelte component.
 *
 * The tag should have a `data-component` attribute with one
 * of the valid values in the Map above.
 */
export class SvelteCustomElement extends HTMLElement {
  component?: SvelteComponent;

  connectedCallback(): void {
    if (this.component) {
      return;
    }
    const type = this.dataset.component;
    const Cls = components.get(type || "");
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
    this.component?.$destroy();
    this.component = undefined;
  }
}
