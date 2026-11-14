<script lang="ts">
  import {
    maybe_open_in_external_editor,
    source_link_for,
  } from "./source-links.ts";

  interface Props {
    file_path: string;
    line: string | number;
    label: string;
    title?: string;
    class_name?: string;
  }

  let { file_path, line, label, title, class_name = "" }: Props = $props();
  let link = $derived(source_link_for(file_path, line));
</script>

{#if link.mode === "command"}
  <a
    class={class_name}
    href={link.href}
    {title}
    onclick={async (event) => {
      event.preventDefault();
      await maybe_open_in_external_editor(link, file_path, line);
    }}
  >
    {label}
  </a>
{:else}
  <a class={class_name} href={link.href} {title}>
    {label}
  </a>
{/if}
