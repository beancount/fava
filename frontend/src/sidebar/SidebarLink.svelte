<script lang="ts">
  import type { KeySpec } from "../keyboard-shortcuts";
  import { keyboardShortcut } from "../keyboard-shortcuts";
  import { base_url } from "../stores";
  import { pathname, synced_query_string } from "../stores/url";

  export let report: string;
  export let name: string;
  export let key: KeySpec | undefined = undefined;
  export let remote: true | undefined = undefined;
  export let bubble: [number, "error" | "info"] | undefined = undefined;

  $: href = remote ? report : `${$base_url}${report}/${$synced_query_string}`;
  $: selected = remote ? false : href.includes($pathname);
</script>

<li>
  <a class:selected {href} use:keyboardShortcut={key} data-remote={remote}>
    {name}
    {#if bubble && bubble[0] > 0}
      <span class="bubble" class:error={bubble[1] === "error"}>
        {bubble[0]}
      </span>
    {/if}
  </a>
  <slot />
</li>

<style>
  a {
    display: block;
    padding: 0.25em 0.5em 0.25em 1em;
    color: inherit;
  }

  a.selected,
  a:hover {
    color: var(--sidebar-hover-color);
    background-color: var(--sidebar-border);
  }

  li {
    display: flex;
    flex-wrap: wrap;
  }

  li:last-child {
    margin-bottom: 0;
    border: none;
  }

  li a:first-child {
    flex: 1;
  }

  .bubble {
    float: right;
    padding: 0 8px;
    font-size: 0.9em;
    color: var(--sidebar-color);
    background-color: var(--sidebar-border);
    border-radius: 12px;
  }

  .error.bubble {
    color: white;
    background-color: var(--error);
  }
</style>
