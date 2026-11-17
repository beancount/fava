<script lang="ts">
  import { type EntryMetadata, RawDecimal } from "../entries/metadata.ts";
  import { _ } from "../i18n.ts";

  interface Props {
    meta: EntryMetadata;
    metadata_key: string;
    value: string;
  }

  let { meta = $bindable(), metadata_key, value }: Props = $props();

  const DECIMAL_RE = /^(?:\+|-)?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE](?:\+|-)?\d+)?$/;
  let stored_value = $derived(meta.get(metadata_key));
  let kind = $derived(
    stored_value instanceof RawDecimal
      ? "number"
      : typeof stored_value === "string"
        ? "text"
        : "auto",
  );
  let input: HTMLInputElement | undefined = $state.raw();

  function set_value(value: string) {
    if (kind === "number") {
      if (DECIMAL_RE.test(value)) {
        meta = meta.set(metadata_key, new RawDecimal(value));
      }
    } else if (kind === "text") {
      meta = meta.set(metadata_key, value);
    } else {
      meta = meta.set_string(metadata_key, value);
    }
  }
</script>

<select
  aria-label={_("Metadata value type")}
  bind:value={
    () => kind,
    (selected: typeof kind) => {
      kind = selected;
      set_value(input?.value ?? value);
    }
  }
>
  <option value="text">{_("Text")}</option>
  <option value="number">{_("Number")}</option>
  <option value="auto">{_("Automatic")}</option>
</select>
<input
  bind:this={input}
  type="text"
  class="value"
  placeholder={_("Value")}
  {value}
  inputmode={kind === "number" ? "decimal" : undefined}
  pattern={kind === "number" ? DECIMAL_RE.source : undefined}
  required={kind === "number"}
  oninput={(event) => {
    if (kind !== "auto") {
      set_value(event.currentTarget.value);
    }
  }}
  onchange={(event) => {
    if (kind === "auto") {
      set_value(event.currentTarget.value);
    }
  }}
/>

<style>
  input {
    flex: 1 1 8rem;
    min-width: 0;
  }
</style>
