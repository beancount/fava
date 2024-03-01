<script lang="ts">
  import type { KeySpec } from "../keyboard-shortcuts";
  import { keyboardShortcut } from "../keyboard-shortcuts";
  import { base_url } from "../stores";
  import { pathname, synced_query_string } from "../stores/url";

  export let report: string;
  export let key: KeySpec | undefined = undefined;
  export let remote: true | undefined = undefined;

  $: href = remote ? report : `${$base_url}${report}/${$synced_query_string}`;
  $: selected = remote ? false : href.includes($pathname);
</script>

<a class:selected {href} use:keyboardShortcut={key} data-remote={remote}>
  <slot />
</a>
