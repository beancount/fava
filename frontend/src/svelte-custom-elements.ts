/**
 * A custom element that will render a Svelte component.
 */

import { type Component, mount, unmount } from "svelte";
import { get as store_get } from "svelte/store";

import type { FavaChart } from "./charts";
import { parseChartData } from "./charts";
import ChartSwitcher from "./charts/ChartSwitcher.svelte";
import { chartContext } from "./charts/context";
import {
  account_hierarchy_validator,
  type AccountTreeNode,
} from "./charts/hierarchy";
import { domHelpers } from "./charts/tooltip";
import type { Result } from "./lib/result";
import { log_error } from "./log";
import type { QueryResultTable } from "./reports/query/query_table";
import { query_table_validator } from "./reports/query/query_table";
import QueryTable from "./reports/query/QueryTable.svelte";
import TreeTable from "./tree-table/TreeTable.svelte";

/** This class pairs the components and their validation functions to use them in a type-safe way. */
class SvelteCustomElementComponent<T extends Record<string, unknown>> {
  constructor(
    readonly type: string,
    private readonly Component: Component<T>,
    private readonly validate: (data: unknown) => Result<T, Error>,
  ) {}

  /** Load data and render the component for this route to the given target. */
  render(target: SvelteCustomElement, data: unknown): (() => void) | undefined {
    const res = this.validate(data);
    if (res.is_err) {
      target.setError(
        `Rendering component '${this.type}' failed due to invalid JSON data:`,
        domHelpers.br(),
        res.error.message,
      );
      log_error(res.error);
      log_error("Invalid JSON for component:", data);
      return undefined;
    }
    const instance = mount(this.Component, { target, props: res.value });
    return () => {
      void unmount(instance);
    };
  }
}

const components = [
  new SvelteCustomElementComponent<{ charts: readonly FavaChart[] }>(
    "charts",
    ChartSwitcher,
    (data) =>
      parseChartData(data, store_get(chartContext)).map((charts) => ({
        charts,
      })),
  ),
  new SvelteCustomElementComponent<{ table: QueryResultTable }>(
    "query-table",
    QueryTable,
    (data) => query_table_validator(data).map((table) => ({ table })),
  ),
  new SvelteCustomElementComponent<{ tree: AccountTreeNode; end: null }>(
    "tree-table",
    TreeTable,
    (data) =>
      account_hierarchy_validator(data).map((tree) => ({ tree, end: null })),
  ),
];

/**
 * A custom element that represents a Svelte component.
 *
 * The tag should have a `type` attribute with one
 * of the valid values in the Map above.
 */
export class SvelteCustomElement extends HTMLElement {
  private destroy?: (() => void) | undefined;

  /** Show some error content. */
  setError(...nodes_or_strings: (Node | string)[]): void {
    this.classList.add("error");
    this.replaceChildren("Error: ", ...nodes_or_strings);
  }

  connectedCallback(): void {
    if (this.destroy) {
      return;
    }
    const type = this.getAttribute("type");
    if (type == null) {
      this.setError("Component is missing type");
      return;
    }
    const comp = components.find((t) => t.type === type);
    if (!comp) {
      this.setError(`Unknown component type: '${type}'`);
      return;
    }
    const script = this.querySelector("script");
    this.destroy = comp.render(
      this,
      script?.type === "application/json" ? JSON.parse(script.innerHTML) : null,
    );
  }

  disconnectedCallback(): void {
    try {
      this.destroy?.();
      this.destroy = undefined;
    } catch {
      // pass
    }
  }
}
