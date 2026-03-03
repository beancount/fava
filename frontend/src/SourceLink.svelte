<script lang="ts">
  import { maybeOpenInExternalEditor, sourceLinkFor } from "./source-links.ts";

  interface Props {
    file_path: string;
    line: string | number;
    label: string;
    title?: string;
    class_name?: string;
  }

  let { file_path, line, label, title, class_name = "" }: Props = $props();
  let link = $derived(sourceLinkFor(file_path, line));
</script>

{#if link.mode === "command"}
  <a
    class={class_name}
    href={link.href}
    {title}
    onclick={async (event) => {
      event.preventDefault();
      const line_string = line.toString();
      const line_number = Number.parseInt(line_string, 10);
      if (!Number.isNaN(line_number)) {
        await maybeOpenInExternalEditor(link, file_path, line);
      }
    }}
  >
    {label}
  </a>
{:else}
  <a class={class_name} href={link.href} {title}>
    {label}
  </a>
{/if}
