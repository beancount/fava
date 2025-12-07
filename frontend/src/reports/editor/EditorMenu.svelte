<script lang="ts">
  import type { EditorView } from "@codemirror/view";
  import type { Snippet } from "svelte";

  import type { CodemirrorBeancount } from "../../codemirror/types.ts";
  import { urlFor } from "../../helpers.ts";
  import { _ } from "../../i18n.ts";
  import { modKey } from "../../keyboard-shortcuts.ts";
  import { router } from "../../router.ts";
  import { insert_entry } from "../../stores/fava_options.ts";
  import { sources } from "../../stores/options.ts";
  import AppMenu from "./AppMenu.svelte";
  import AppMenuItem from "./AppMenuItem.svelte";
  import AppMenuSubItem from "./AppMenuSubItem.svelte";
  import Key from "./Key.svelte";

  interface Props {
    file_path: string;
    editor: EditorView;
    codemirror_beancount: CodemirrorBeancount;
    children: Snippet;
  }

  let { file_path, editor, codemirror_beancount, children }: Props = $props();

  function goToFileAndLine(filename: string, line?: number) {
    const url = $urlFor("editor/", { file_path: filename, line });
    // only load if the file changed.
    const load = filename !== file_path;
    router.navigate(url, load);
    if (!load && line != null) {
      // Scroll to line if we didn't change to a different file.
      editor.dispatch(codemirror_beancount.scroll_to_line(editor.state, line));
      editor.focus();
    }
  }
</script>

<div>
  <AppMenu>
    <AppMenuItem name={_("File")}>
      {#each $sources as source (source)}
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
      <AppMenuSubItem
        action={() => codemirror_beancount.beancount_format(editor)}
      >
        {_("Align Amounts")}
        {#snippet right()}
          <Key key={[modKey, "d"]} />
        {/snippet}
      </AppMenuSubItem>
      <AppMenuSubItem action={() => codemirror_beancount.toggleComment(editor)}>
        {_("Toggle Comment (selection)")}
        {#snippet right()}
          <Key key={[modKey, "/"]} />
        {/snippet}
      </AppMenuSubItem>
      <AppMenuSubItem action={() => codemirror_beancount.unfoldAll(editor)}>
        {_("Open all folds")}
        {#snippet right()}
          <Key key={["Ctrl", "Alt", "]"]} />
        {/snippet}
      </AppMenuSubItem>
      <AppMenuSubItem action={() => codemirror_beancount.foldAll(editor)}>
        {_("Close all folds")}
        {#snippet right()}
          <Key key={["Ctrl", "Alt", "["]} />
        {/snippet}
      </AppMenuSubItem>
    </AppMenuItem>
    {#if $insert_entry.length}
      <AppMenuItem name={`'insert-entry' ${_("Options")}`}>
        {#each $insert_entry as opt (`${opt.filename}:${opt.lineno.toString()}`)}
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
