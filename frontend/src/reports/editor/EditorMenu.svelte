<script lang="ts">
  import { toggleComment } from "@codemirror/commands";
  import { foldAll, unfoldAll } from "@codemirror/language";
  import type { EditorView } from "@codemirror/view";

  import { beancountFormat } from "../../codemirror/beancount-format";
  import { scrollToLine } from "../../codemirror/editor-transactions";
  import { urlFor } from "../../helpers";
  import { _ } from "../../i18n";
  import { modKey } from "../../keyboard-shortcuts";
  import router from "../../router";
  import { fava_options, options } from "../../stores";
  import AppMenu from "./AppMenu.svelte";
  import AppMenuItem from "./AppMenuItem.svelte";
  import AppMenuSubItem from "./AppMenuSubItem.svelte";
  import Key from "./Key.svelte";

  export let file_path: string;
  export let editor: EditorView;

  $: sources = [
    $options.filename,
    ...$options.include.filter((f) => f !== $options.filename),
  ];
  $: insertEntryOptions = $fava_options.insert_entry;

  function goToFileAndLine(filename: string, line?: number) {
    const url = urlFor("editor/", { file_path: filename, line });
    router.navigate(url);
    if (filename === file_path && line != null) {
      editor.dispatch(scrollToLine(editor.state, line));
      editor.focus();
    }
  }
</script>

<div>
  <AppMenu>
    <AppMenuItem name={_("File")}>
      {#each sources as source}
        <AppMenuSubItem
          action={() => {
            goToFileAndLine(source);
          }}
          selected={source === file_path}
        >
          {source}
        </AppMenuSubItem>
      {/each}
    </AppMenuItem>
    <AppMenuItem name={_("Edit")}>
      <AppMenuSubItem action={() => beancountFormat(editor)}>
        {_("Align Amounts")}
        <Key slot="right" key={[modKey, "d"]} />
      </AppMenuSubItem>
      <AppMenuSubItem action={() => toggleComment(editor)}>
        {_("Toggle Comment (selection)")}
        <Key slot="right" key={[modKey, "/"]} />
      </AppMenuSubItem>
      <AppMenuSubItem action={() => unfoldAll(editor)}>
        {_("Open all folds")}
        <Key slot="right" key={["Ctrl", "Alt", "]"]} />
      </AppMenuSubItem>
      <AppMenuSubItem action={() => foldAll(editor)}>
        {_("Close all folds")}
        <Key slot="right" key={["Ctrl", "Alt", "["]} />
      </AppMenuSubItem>
    </AppMenuItem>
    {#if insertEntryOptions.length}
      <AppMenuItem name={`'insert-entry' ${_("Options")}`}>
        {#each insertEntryOptions as opt}
          <AppMenuSubItem
            title={`${opt.filename}:${opt.lineno.toString()}`}
            action={() => {
              goToFileAndLine(opt.filename, opt.lineno - 1);
            }}
          >
            {opt.re}
            <span slot="right">{opt.date}</span>
          </AppMenuSubItem>
        {/each}
      </AppMenuItem>
    {/if}
  </AppMenu>
  <slot />
</div>

<style>
  div {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    background: var(--sidebar-background);
    border-bottom: 1px solid var(--sidebar-border);
  }
</style>
