/**
 * A custom element that will render a Svelte component.
 */

import { SvelteComponent } from "svelte";

import ChartSwitcher from "./charts/ChartSwitcher.svelte";
import Documents from "./documents/Documents.svelte";
import SourceEditor from "./editor/SourceEditor.svelte";
import FilterForm from "./header/FilterForm.svelte";
import Import from "./import/Import.svelte";
import Modals from "./modals/Modals.svelte";
import Query from "./query/Query.svelte";
import AccountSelector from "./sidebar/AccountSelector.svelte";

const components = new Map([
  ["charts", ChartSwitcher],
  ["documents", Documents],
  ["editor", SourceEditor],
  ["import", Import],
  ["query", Query],
  ["account-selector", AccountSelector],
  ["filter-form", FilterForm],
  ["modals", Modals],
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
    this.component?.$destroy();
    this.component = undefined;
  }
}
