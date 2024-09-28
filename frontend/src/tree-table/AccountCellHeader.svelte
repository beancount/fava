<!--
    @component
    Header for the account column.
-->
<script lang="ts">
  import { _ } from "../i18n";
  import { getTreeTableContext } from "./helpers";

  const { toggled } = getTreeTableContext();

  const help_title = _(
    "Hold Shift while clicking to expand all children.\n" +
      "Hold Ctrl or Cmd while clicking to expand one level.",
  );
</script>

<span title={help_title}>
  {#if $toggled.size}
    <button
      type="button"
      class="link"
      title={_("Expand all accounts")}
      on:click={() => {
        toggled.set(new Set());
      }}
    >
      {_("Expand all")}
    </button>
  {/if}
</span>

<style>
  span {
    flex: 1;
    min-width: 14em;
    max-width: 30em;
  }

  button {
    margin-left: 1em;
    font-weight: normal;
    color: inherit;
    opacity: 0.5;
  }
</style>
