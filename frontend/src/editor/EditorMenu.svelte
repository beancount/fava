<script lang="ts">
  import { toggleComment } from "@codemirror/comment";
  import { foldAll, unfoldAll } from "@codemirror/fold";
  import type { EditorView } from "@codemirror/view";
  import path from "path-browserify";

  import { beancountFormat } from "../codemirror/beancount-format";
  import { scrollToLine } from "../codemirror/scroll-to-line";
  import { urlFor } from "../helpers";
  import { _ } from "../i18n";
  import { modKey } from "../keyboard-shortcuts";
  import router from "../router";
  import { favaOptions, options } from "../stores";

  import Folder from "./Folder.svelte";
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

  function _dummy_folder(name: string, sub_node) {
    if ("subfolders" in sub_node) {
      return { name, subfolders: [sub_node], subfiles: [] };
    }
    return { name, subfolders: [], subfiles: [sub_node] };
  }
  function dummy_folder(path_str: string) {
    let p = path.parse(path_str);
    let folder_path = p.dir;
    const { root } = p;

    const file_node = { name: p.base, path: path_str };
    let last_node = file_node;
    while (folder_path !== root) {
      p = path.parse(folder_path);
      last_node = _dummy_folder(p.base, last_node);
      folder_path = p.dir;
    }
    return _dummy_folder(root, last_node);
  }
  function shorten_folder(folder) {
    // Flatten the nested folder when possible.
    if (folder.subfiles.length === 0 && folder.subfolders.length === 1) {
      const subfolder = folder.subfolders[0];
      const new_name = path.join(folder.name, subfolder.name);
      return shorten_folder({
        name: new_name,
        subfolders: subfolder.subfolders,
        subfiles: subfolder.subfiles,
      });
    }
    return {
      name: folder.name,
      subfolders: folder.subfolders.map(shorten_folder),
      subfiles: folder.subfiles,
    };
  }
  let merge_folder;
  function merge_same_name_folder(name: string, i_folders: []) {
    if (i_folders.length === 1) {
      return i_folders[0];
    }
    return {
      name,
      subfolders: merge_folder(i_folders.map((o) => o.subfolders).flat()),
      subfiles: i_folders.map((o) => o.subfiles).flat(),
    };
  }
  function groupBy(xs: [], key: string) {
    return xs.reduce((rv, x) => {
      (rv[x[key]] = rv[x[key]] || []).push(x);
      return rv;
    }, {});
  }
  merge_folder = (i_folders: []): [] => {
    const dict = groupBy(
      i_folders.sort((a, b) => {
        if (a.name === b.name) {
          return 0;
        }
        return a.name > b.name ? 1 : -1;
      }),
      "name"
    );
    return Object.entries(dict).map(([name, group]) =>
      merge_same_name_folder(name, group)
    );
  };
  function source_tree(files: string[]): [] {
    return merge_folder(files.map(dummy_folder)).map(shorten_folder);
  }
  $: folders = source_tree(sources);
</script>

<div class="fieldset">
  <div class="dropdown">
    <span>
      {_("File")}
      <ul>
        {#each folders as folder}
          <Folder {folder} {file_path} expanded />
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
