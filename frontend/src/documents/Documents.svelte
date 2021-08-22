<script lang="ts">
  import { moveDocument } from "../api";
  import AccountInput from "../entry-forms/AccountInput.svelte";
  import { _ } from "../i18n";
  import { basename } from "../lib/paths";
  import { stratify } from "../lib/tree";
  import ModalBase from "../modals/ModalBase.svelte";
  import router from "../router";

  import Accounts from "./Accounts.svelte";
  import DocumentPreview from "./DocumentPreview.svelte";
  import Table from "./Table.svelte";

  type Document = { account: string; filename: string; date: string };
  type MoveDetails = { account: string; filename: string; newName: string };

  export let data: Document[];

  $: node = stratify(
    new Set(data.map((e) => e.account)),
    (s) => s,
    (name) => ({ name })
  );

  let selected: Document;
  let moving: MoveDetails | null = null;

  /**
   * Rename the selected document with <F2>.
   */
  function keyup(ev: KeyboardEvent) {
    if (ev.key === "F2" && selected) {
      moving = { ...selected, newName: basename(selected.filename) };
    }
  }

  async function move() {
    const moved =
      moving &&
      (await moveDocument(moving.filename, moving.account, moving.newName));
    if (moved) {
      moving = null;
      router.reload();
    }
  }
</script>

<svelte:window on:keyup={keyup} />
{#if moving}
  <ModalBase
    shown={true}
    closeHandler={() => {
      moving = null;
    }}
  >
    <div>
      <h3>{_("Move or rename document")}</h3>
      <p><code>{moving.filename}</code></p>
      <p>
        <AccountInput bind:value={moving.account} />
        <input size={40} bind:value={moving.newName} />
        <button type="button" on:click={move}>{"Move"}</button>
      </p>
    </div>
  </ModalBase>
{/if}
<div class="fixed-fullsize-container">
  <Accounts
    {node}
    move={(arg) => {
      moving = { ...arg, newName: basename(arg.filename) };
    }}
  />
  <div>
    <Table bind:selected {data} />
  </div>
  {#if selected}
    <DocumentPreview filename={selected.filename} />
  {/if}
</div>

<style>
  .fixed-fullsize-container {
    display: grid;
    grid-template-columns: 1fr 2fr 3fr;
  }
  .fixed-fullsize-container > :global(*) {
    height: 100%;
    overflow: auto;
    resize: horizontal;
  }
  .fixed-fullsize-container > :global(* + *) {
    border-left: thin solid var(--color-sidebar-border);
  }
</style>
