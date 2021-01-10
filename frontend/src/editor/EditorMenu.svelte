<script>
  import { createEventDispatcher } from "svelte";

  import { _ } from "../i18n";
  import { urlFor } from "../helpers";

  /** @type {string[]} */
  export let sources;
  /** @type {string} */
  export let file_path;

  const dispatch = createEventDispatcher();
</script>

<div class="fieldset">
  <ul class="dropdown">
    <li>
      {_("File")}&nbsp;▾

      <ul>
        {#each sources as source}
          <li class:selected={source === file_path}>
            <a href={urlFor("editor", { file_path: source })}>{source}</a>
          </li>
        {/each}
      </ul>
    </li>
    <li>
      {_("Edit")}
      &nbsp;▾
      <ul>
        <li on:click={() => dispatch("command", "favaFormat")}>
          {_("Align Amounts")}
          <span> <kbd>Ctrl</kbd> / <kbd>Cmd</kbd> + <kbd>d</kbd> </span>
        </li>
        <li on:click={() => dispatch("command", "favaToggleComment")}>
          {_("Toggle Comment (selection)")}
          <span> <kbd>Ctrl</kbd> / <kbd>Cmd</kbd> + <kbd>y</kbd> </span>
        </li>
        <li on:click={() => dispatch("command", "unfoldAll")}>
          {_("Open all folds")}
        </li>
        <li on:click={() => dispatch("command", "foldAll")}>
          {_("Close all folds")}
        </li>
      </ul>
    </li>
  </ul>
  <slot />
</div>

<style>
  li {
    cursor: pointer;
  }

  .fieldset {
    height: var(--source-editor-fieldset-height);
    padding-left: 0.5em;
    border-bottom: 1px solid var(--color-sidebar-border);
  }

  .dropdown {
    display: flex;
    height: 100%;
    margin: 0;
  }

  .dropdown .selected::before {
    content: "›";
  }

  .dropdown > li {
    position: relative;
    height: var(--source-editor-fieldset-height);
    margin-right: 10px;
    line-height: var(--source-editor-fieldset-height);
    cursor: default;
  }

  .dropdown > li > ul {
    position: absolute;
    top: var(--source-editor-fieldset-height);
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

  .dropdown > li > ul > li {
    padding: 2px 10px;
  }

  .dropdown > li > ul > li span {
    float: right;
  }

  .dropdown li:hover > ul {
    display: block;
  }
</style>
