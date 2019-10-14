<script>
  import { moveDocument } from "../api";
  import { favaAPI } from "../stores";
  import { _ } from "../helpers";
  import router from "../router";

  import { basename, entriesToTree } from "./util";

  import AccountInput from "../entry-forms/AccountInput.svelte";
  import ModalBase from "../modals/ModalBase.svelte";
  import Accounts from "./Accounts.svelte";
  import Table from "./Table.svelte";

  export let data;
  let selected;
  let moving = null;

  /**
   * Rename the selected document with <F2>.
   */
  function keyup(ev) {
    if (ev.key === "F2" && selected) {
      moving = {
        account: selected.account,
        filename: selected.filename,
        newName: basename(selected.filename),
      };
    }
  }

  /**
   * Move a document to the account it is dropped on.
   */
  function drop(ev) {
    moving = {
      account: ev.detail.account,
      filename: ev.detail.filename,
      newName: basename(ev.detail.filename),
    };
  }

  async function move() {
    const moved = await moveDocument(
      moving.filename,
      moving.account,
      moving.newName
    );
    if (moved) {
      moving = null;
      router.reload();
    }
  }
</script>

<style>
  .container {
    display: flex;
    position: fixed;
    top: var(--header-height);
    right: 0;
    bottom: 0;
    left: var(--aside-width);
  }
  .half-column {
    width: 33%;
    height: 100%;
    overflow: auto;
    resize: horizontal;
    border-right: thin solid var(--color-sidebar-border);
  }
</style>

<svelte:window on:keyup={keyup} />
{#if moving}
  <ModalBase
    shown={true}
    closeHandler={() => {
      moving = null;
    }}>
    <div>
      <h3>{_('Move or rename document')}</h3>
      <p>
        <code>{moving.filename}</code>
      </p>
      <p>
        <AccountInput bind:value={moving.account} />
        <input size="40" bind:value={moving.newName} />
        <button type="button" on:click={move}>{'Move'}</button>
      </p>
    </div>
  </ModalBase>
{/if}
<div class="container">
  <div class="half-column" style="width: 14rem;">
    <Accounts node={entriesToTree(data)} on:drop={drop} />
  </div>
  <div class="half-column">
    <Table bind:selected {data} />
  </div>
  <div style="flex: 1;">
    {#if selected}
      <object
        title={selected.filename}
        data={`${favaAPI.baseURL}document/?filename=${selected.filename}`}
        style="width:100%;height:100%" />
    {/if}
  </div>
</div>
