<script>
  import { moveDocument } from "../api";
  import { baseURL } from "../stores/url";
  import { _ } from "../i18n";
  import router from "../router";

  import { basename } from "../lib/paths";
  import { entriesToTree } from "./util";

  import AccountInput from "../entry-forms/AccountInput.svelte";
  import ModalBase from "../modals/ModalBase.svelte";
  import Accounts from "./Accounts.svelte";
  import Table from "./Table.svelte";

  /** @typedef {{account: string, filename: string, date: string}} Document */

  /** @type {Document[]} */
  export let data;

  /** @type {Document} */
  let selected;
  /** @type {{account: string, filename: string, newName: string} | null} */
  let moving = null;

  /**
   * @param {Document} doc
   */
  function copyMoveable(doc) {
    return {
      account: doc.account,
      filename: doc.filename,
      newName: basename(doc.filename),
    };
  }

  /**
   * Rename the selected document with <F2>.
   * @param {KeyboardEvent} ev
   */
  function keyup(ev) {
    if (ev.key === "F2" && selected) {
      moving = copyMoveable(selected);
    }
  }

  /**
   * Move a document to the account it is dropped on.
   * @param {CustomEvent} ev
   */
  function drop(ev) {
    moving = copyMoveable(ev.detail);
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

<style>
  .container {
    position: fixed;
    top: var(--header-height);
    right: 0;
    bottom: 0;
    left: var(--aside-width);
    display: flex;
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
      <p><code>{moving.filename}</code></p>
      <p>
        <AccountInput bind:value={moving.account} />
        <input size={40} bind:value={moving.newName} />
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
        data={`${$baseURL}document/?filename=${selected.filename}`}
        style="width:100%;height:100%" />
    {/if}
  </div>
</div>
