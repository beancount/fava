<script lang="ts">
  import { hideHeader } from "../stores";
  import AsideWithButton from "./AsideWithButton.svelte";
  import Header from "./Header.svelte";
</script>

{#if !$hideHeader}
  <Header />
{/if}
<AsideWithButton />
