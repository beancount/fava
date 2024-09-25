<script lang="ts">
  import { group } from "d3-array";

  import { moveDocument } from "../../api";
  import type { Document } from "../../entries";
  import AccountInput from "../../entry-forms/AccountInput.svelte";
  import { _ } from "../../i18n";
  import { basename } from "../../lib/paths";
  import { stratify } from "../../lib/tree";
  import ModalBase from "../../modals/ModalBase.svelte";
  import router from "../../router";
  import Accounts from "./Accounts.svelte";
  import DocumentPreview from "./DocumentPreview.svelte";
  import Table from "./Table.svelte";

  export let documents: Document[];

  interface MoveDetails {
    account: string;
    filename: string;
    newName: string;
  }

  $: grouped = group(documents, (d) => d.account);
  $: node = stratify(
    grouped.entries(),
    ([s]) => s,
    (name, d) => ({ name, count: d?.[1].length ?? 0 }),
  );

  let selected: Document | null = null;
  let moving: MoveDetails | null = null;

  /**
   * Rename the selected document with <F2>.
   */
  function keyup(ev: KeyboardEvent) {
    if (ev.key === "F2" && selected && !moving) {
      moving = { ...selected, newName: basename(selected.filename) };
    }
  }

  async function move() {
    if (moving) {
      const moved = await moveDocument(
        moving.filename,
        moving.account,
        moving.newName,
      );
      if (moved) {
        moving = null;
        router.reload();
      }
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
    <form on:submit|preventDefault={move}>
      <h3>{_("Move or rename document")}</h3>
      <p><code>{moving.filename}</code></p>
      <p>
        <AccountInput bind:value={moving.account} />
        <input size={40} bind:value={moving.newName} />
        <button type="submit">{"Move"}</button>
      </p>
    </form>
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
    <Table bind:selected data={documents} />
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
    border-left: thin solid var(--sidebar-border);
  }
</style>
