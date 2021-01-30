<script>
  import { toggleComment } from "@codemirror/comment";
  import { foldAll, unfoldAll } from "@codemirror/fold";

  import { _ } from "../i18n";
  import { urlFor } from "../helpers";

  import { beancountFormat } from "../codemirror/beancount-format";
  import { modKey } from "../keyboard-shortcuts";
  import Key from "./Key.svelte";
  import { favaAPIStore } from "../stores";

  /** @type {string} */
  export let file_path;

  /** @type {(c: import("@codemirror/view").Command) => void} */
  export let onCommand;

  $: options = $favaAPIStore.options;
  $: sources = [
    options.filename,
    ...options.include.filter((f) => f !== options.filename),
  ];
</script>

<div class="fieldset">
  <div class="dropdown">
    <span>
      {_("File")}
      <ul>
        {#each sources as source}
          <li class:selected={source === file_path}>
            <a href={urlFor("editor", { file_path: source })}>{source}</a>
          </li>
        {/each}
      </ul>
    </span>
    <span>
      {_("Edit")}
      <ul>
        <li on:click={() => onCommand(beancountFormat)}>
          {_("Align Amounts")}
          <span><Key key={`${modKey}+d`} /></span>
        </li>
        <li on:click={() => onCommand(toggleComment)}>
          {_("Toggle Comment (selection)")}
          <span><Key key={`${modKey}+/`} /></span>
        </li>
        <li on:click={() => onCommand(unfoldAll)}>
          {_("Open all folds")}
          <span><Key key="Ctrl+Alt+]" /></span>
        </li>
        <li on:click={() => onCommand(foldAll)}>
          {_("Close all folds")}
          <span><Key key="Ctrl+Alt+[" /></span>
        </li>
      </ul>
    </span>
  </div>
  <slot />
</div>

<style>
  li {
    cursor: pointer;
  }

  .fieldset {
    height: 3rem;
    background: var(--color-sidebar-background);
    border-bottom: 1px solid var(--color-sidebar-border);
  }

  .dropdown {
    display: flex;
    gap: 0.5rem;
    align-items: stretch;
    height: 100%;
    margin-right: 0.5rem;
  }

  .dropdown .selected::before {
    content: "›";
  }

  .dropdown > span {
    padding: 0.75rem 0.5rem;
    cursor: pointer;
  }

  .dropdown > span::after {
    content: "▾";
  }

  .dropdown > span > ul {
    position: absolute;
    top: 3rem;
    z-index: var(--z-index-floating-ui);
    display: none;
    width: 500px;
    max-height: 400px;
    margin-left: -10px;
    overflow-y: auto;
    line-height: 1.5;
    background-color: var(--color-background);
    border: 1px solid var(--color-background-darker);
    border-bottom-right-radius: 3px;
    border-bottom-left-radius: 3px;
    box-shadow: 0 3px 6px var(--color-transparent-black);
  }

  .dropdown > span > ul > li {
    padding: 2px 10px;
  }

  .dropdown > span > ul > li span {
    float: right;
  }

  .dropdown li:hover,
  .dropdown > span:hover {
    background-color: var(--color-background-darkest);
  }

  .dropdown > span:hover > ul {
    display: block;
  }
</style>
