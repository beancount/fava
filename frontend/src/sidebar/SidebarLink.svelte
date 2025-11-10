<script lang="ts">
  import type { Snippet } from "svelte";

  import { urlFor } from "../helpers.ts";
  import type { KeySpec } from "../keyboard-shortcuts.ts";
  import { keyboardShortcut } from "../keyboard-shortcuts.ts";
  import { pathname } from "../stores/url.ts";

  interface Props {
    /** Report to generate the URL for. */
    report: string;
    /** Name to display for this link. */
    name: string;
    /** Key combination for the link. */
    key?: KeySpec;
    /** Whether this is a remote link (for which we do not intercept clicks). */
    remote?: true;
    /** Show a bubble with a number */
    bubble?: [number, "error" | "info"];
    children?: Snippet;
  }

  let { report, name, key, remote, bubble, children }: Props = $props();

  let href = $derived(remote ? report : $urlFor(`${report}/`));
  let selected = $derived(remote ? false : href.includes($pathname));
</script>

<li>
  <a class:selected {href} {@attach keyboardShortcut(key)} data-remote={remote}>
    {name}
    {#if bubble && bubble[0] > 0}
      <span class="bubble" class:error={bubble[1] === "error"}>
        {bubble[0]}
      </span>
    {/if}
  </a>
  {@render children?.()}
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
