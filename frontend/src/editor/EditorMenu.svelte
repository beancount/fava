<script lang="ts">
  import { toggleComment } from "@codemirror/commands";
  import { foldAll, unfoldAll } from "@codemirror/language";
  import type { EditorView } from "@codemirror/view";

  import { beancountFormat } from "../codemirror/beancount-format";
  import { scrollToLine } from "../codemirror/scroll-to-line";
  import { urlFor } from "../helpers";
  import { _ } from "../i18n";
  import { modKey } from "../keyboard-shortcuts";
  import router from "../router";
  import { favaOptions, options } from "../stores";

  import Key from "./Key.svelte";

  export let file_path: string;
  export let editor: EditorView;

  $: sources = [
    $options.filename,
    ...$options.include.filter((f) => f !== $options.filename),
  ];
  $: insertEntryOptions = $favaOptions.insert_entry;

  function goToFileAndLine(filename: string, line?: number) {
    const url = urlFor("editor/", { file_path: filename, line });
    const shouldLoad = filename !== file_path;
    router.navigate(url, shouldLoad);
    if (!shouldLoad && line) {
      scrollToLine(editor, line);
      editor.focus();
    }
  }
</script>

<div class="fieldset">
  <div class="dropdown">
    <span tabindex="0" role="menu">
      {_("File")}
      <ul>
        {#each sources as source}
          <li class:selected={source === file_path}>
            <button on:click={() => goToFileAndLine(source)}>
              {source}
            </button>
          </li>
        {/each}
      </ul>
    </span>
    <span tabindex="0" role="menu">
      {_("Edit")}
      <ul>
        <li>
          <button on:click={() => beancountFormat(editor)}>
            {_("Align Amounts")}
            <span><Key key={`${modKey}+d`} /></span>
          </button>
        </li>
        <li>
          <button on:click={() => toggleComment(editor)}>
            {_("Toggle Comment (selection)")}
            <span><Key key={`${modKey}+/`} /></span>
          </button>
        </li>
        <li>
          <button on:click={() => unfoldAll(editor)}>
            {_("Open all folds")}
            <span><Key key="Ctrl+Alt+]" /></span>
          </button>
        </li>
        <li>
          <button on:click={() => foldAll(editor)}>
            {_("Close all folds")}
            <span><Key key="Ctrl+Alt+[" /></span>
          </button>
        </li>
      </ul>
    </span>
    {#if insertEntryOptions.length}
      <span tabindex="0" role="menu">
        <code>insert-entry</code>
        {_("Options")}
        <ul>
          {#each insertEntryOptions as opt}
            <li title={`${opt.filename}:${opt.lineno}`}>
              <button
                on:click={() => goToFileAndLine(opt.filename, opt.lineno - 1)}
              >
                {opt.re} <span>{opt.date}</span>
              </button>
            </li>
          {/each}
        </ul>
      </span>
    {/if}
  </div>
  <slot />
</div>

<style>
  .fieldset {
    height: 3rem;
    background: var(--sidebar-background);
    border-bottom: 1px solid var(--sidebar-border);
  }

  .dropdown {
    display: flex;
    gap: 0.5rem;
    align-items: stretch;
    height: 100%;
    margin-right: 0.5rem;
  }

  .selected::before {
    content: "›";
  }

  li {
    padding: 2px 10px;
    cursor: pointer;
  }

  li span {
    float: right;
  }

  .dropdown > span {
    padding: 0.7rem 0.5rem;
    cursor: pointer;
  }

  .dropdown > span::after {
    content: "▾";
  }

  ul {
    position: absolute;
    z-index: var(--z-index-floating-ui);
    display: none;
    width: 500px;
    max-height: 400px;
    margin: 0.75rem 0 0 -0.5rem;
    overflow-y: auto;
    background-color: var(--background);
    border: 1px solid var(--border);
    border-bottom-right-radius: 3px;
    border-bottom-left-radius: 3px;
    box-shadow: 0 3px 6px var(--transparent-black);
  }

  li button {
    display: contents;
    color: inherit;
  }

  li:hover,
  li:focus-visible,
  span:hover {
    background-color: var(--background-darker);
  }

  span:focus-within > ul,
  span:hover > ul {
    display: block;
  }
</style>
