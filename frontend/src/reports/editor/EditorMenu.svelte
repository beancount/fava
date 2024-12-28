<script lang="ts">
  import { toggleComment } from "@codemirror/commands";
  import { foldAll, unfoldAll } from "@codemirror/language";
  import type { EditorView } from "@codemirror/view";
  import type { Snippet } from "svelte";

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

  interface Props {
    file_path: string;
    editor: EditorView;
    children: Snippet;
  }

  let { file_path, editor, children }: Props = $props();

  let sources = $derived([
    $options.filename,
    ...$options.include.filter((f) => f !== $options.filename),
  ]);
  let insertEntryOptions = $derived($fava_options.insert_entry);

  function goToFileAndLine(filename: string, line?: number) {
    const url = $urlFor("editor/", { file_path: filename, line });
    // only load if the file changed.
    const load = filename !== file_path;
    router.navigate(url, load);
    if (!load && line != null) {
      // Scroll to line if we didn't change to a different file.
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
        {#snippet right()}
          <Key key={[modKey, "d"]} />
        {/snippet}
      </AppMenuSubItem>
      <AppMenuSubItem action={() => toggleComment(editor)}>
        {_("Toggle Comment (selection)")}
        {#snippet right()}
          <Key key={[modKey, "/"]} />
        {/snippet}
      </AppMenuSubItem>
      <AppMenuSubItem action={() => unfoldAll(editor)}>
        {_("Open all folds")}
        {#snippet right()}
          <Key key={["Ctrl", "Alt", "]"]} />
        {/snippet}
      </AppMenuSubItem>
      <AppMenuSubItem action={() => foldAll(editor)}>
        {_("Close all folds")}
        {#snippet right()}
          <Key key={["Ctrl", "Alt", "["]} />
        {/snippet}
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
            {#snippet right()}
              <span>{opt.date}</span>
            {/snippet}
          </AppMenuSubItem>
        {/each}
      </AppMenuItem>
    {/if}
  </AppMenu>
  {@render children()}
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
