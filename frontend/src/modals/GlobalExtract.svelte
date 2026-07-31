<script lang="ts">
  import { get_extract, save_entries } from "../api/index.ts";
  import type { Entry } from "../entries/index.ts";
  import { is_non_empty } from "../lib/array.ts";
  import { notify, notify_err } from "../notifications.ts";
  import Extract from "../reports/import/Extract.svelte";
  import { loading_state, router } from "../router.ts";
  import { hash } from "../stores/url.ts";

  let shown = $derived($hash.startsWith("extract?"));

  let extract_params = $derived(
    shown ? new URLSearchParams($hash.slice(8)) : null,
  );
  let filename = $derived(extract_params?.get("filename"));
  let importer = $derived(extract_params?.get("importer"));

  let entries = $state<Entry[]>([]);

  $effect(() => {
    let active = true;

    if (shown) {
      if (filename != null && importer != null) {
        void loading_state
          .await(get_extract({ filename, importer }))
          .then((res) => {
            if (!active) {
              return;
            }
            if (res.length > 0) {
              entries = res;
            } else {
              notify("No entries to import from this file.", "warning");
              close();
            }
          })
          .catch((err: unknown) => {
            if (!active) {
              return;
            }
            notify_err(err);
            close();
          });
      } else {
        close();
      }
    } else {
      entries = [];
    }

    return () => {
      active = false;
    };
  });

  function close() {
    router.close_overlay();
  }

  async function save() {
    const without_duplicates = entries.filter((e) => !e.is_duplicate());
    close();

    if (is_non_empty(without_duplicates)) {
      await save_entries(without_duplicates);
    }
  }
</script>

{#if shown && entries.length > 0}
  <Extract bind:entries {close} {save} />
{/if}
