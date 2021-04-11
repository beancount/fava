<script lang="ts">
  import { toggleComment } from "@codemirror/comment";
  import { foldAll, unfoldAll } from "@codemirror/fold";
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
  $: insertEntryOptions = $favaOptions["insert-entry"];

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
    <span>
      {_("File")}
      <ul>
        {#each sources as source}
          <li
            class:selected={source === file_path}
            on:click={() => goToFileAndLine(source)}
          >
            {source}
          </li>
        {/each}
      </ul>
    </span>
    <span>
      {_("Edit")}
      <ul>
        <li on:click={() => beancountFormat(editor)}>
          {_("Align Amounts")}
          <span><Key key={`${modKey}+d`} /></span>
        </li>
        <li on:click={() => toggleComment(editor)}>
          {_("Toggle Comment (selection)")}
          <span><Key key={`${modKey}+/`} /></span>
        </li>
        <li on:click={() => unfoldAll(editor)}>
          {_("Open all folds")}
          <span><Key key="Ctrl+Alt+]" /></span>
        </li>
        <li on:click={() => foldAll(editor)}>
          {_("Close all folds")}
          <span><Key key="Ctrl+Alt+[" /></span>
        </li>
      </ul>
    </span>
    {#if insertEntryOptions.length}
      <span>
        <code>insert-entry</code>
        {_("Options")}
        <ul>
          {#each insertEntryOptions as opt}
            <li
              on:click={() => goToFileAndLine(opt.filename, opt.lineno - 1)}
              title={`${opt.filename}:${opt.lineno}`}
            >
              {opt.re} <span>{opt.date}</span>
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
    background-color: var(--color-background);
    border: 1px solid var(--color-background-darker);
    border-bottom-right-radius: 3px;
    border-bottom-left-radius: 3px;
    box-shadow: 0 3px 6px var(--color-transparent-black);
  }

  li:hover,
  span:hover {
    background-color: var(--color-background-darkest);
  }

  span:hover > ul {
    display: block;
  }
</style>
