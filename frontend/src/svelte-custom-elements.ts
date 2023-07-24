/**
 * A custom element that will render a Svelte component.
 */

import type { SvelteComponent } from "svelte";
import { get as store_get } from "svelte/store";

import { parseChartData } from "./charts";
import ChartSwitcher from "./charts/ChartSwitcher.svelte";
import { chartContext } from "./charts/context";
import { ok, type Result } from "./lib/result";

/** This class pairs the components and their validation functions to use them in a type-safe way. */
class SvelteCustomElementComponent<
  T extends Record<string, unknown> = Record<string, unknown>,
> {
  constructor(
    private readonly Component: typeof SvelteComponent<T>,
    private readonly validate: (data: unknown) => Result<T, string>,
  ) {}

  /** Load data and render the component for this route to the given target. */
  render(target: HTMLElement, data: unknown): (() => void) | undefined {
    const res = this.validate(data);
    if (!res.success) {
      target.innerHTML = `Rendering component failed: ${res.value}`;
      return undefined;
    }
    const instance = new this.Component({ target, props: res.value });
    return () => {
      instance.$destroy();
    };
  }
}

const components = new Map<string, SvelteCustomElementComponent>([
  [
    "charts",
    new SvelteCustomElementComponent(ChartSwitcher, (data) => {
      const res = parseChartData(data, store_get(chartContext));
      if (res.success) {
        return ok({ charts: res.value });
      }
      return res;
    }),
  ],
]);

/**
 * A custom element that represents a Svelte component.
 *
 * The tag should have a `type` attribute with one
 * of the valid values in the Map above.
 */
export class SvelteCustomElement extends HTMLElement {
  private destroy?: () => void;

  connectedCallback(): void {
    if (this.destroy) {
      return;
    }
    const type = this.getAttribute("type");
    if (!type) {
      throw new Error("Component is missing type");
    }
    const comp = components.get(type);
    if (!comp) {
      throw new Error("Invalid component");
    }
    const script = this.querySelector("script");
    this.destroy = comp.render(
      this,
      script && script.type === "application/json"
        ? JSON.parse(script.innerHTML)
        : null,
    );
  }

  disconnectedCallback(): void {
    try {
      this.destroy?.();
      this.destroy = undefined;
    } catch (e) {
      // pass
    }
  }
}
