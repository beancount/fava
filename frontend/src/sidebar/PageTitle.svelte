<script lang="ts">
  import { log_error } from "../log.ts";
  import AccountPageTitle from "./AccountPageTitle.svelte";
  import { page_title } from "./page-title.ts";

  let { title, type } = $derived($page_title);

  let is_account = $derived(type === "account");
  let copied = $state(false);
  let copied_timeout: ReturnType<typeof setTimeout> | undefined;

  async function copyAccountTitle(event: MouseEvent): Promise<void> {
    event.stopPropagation();

    try {
      await navigator.clipboard.writeText(title);
      copied = true;

      clearTimeout(copied_timeout);
      copied_timeout = setTimeout(() => {
        copied = false;
      }, 1500);
    } catch (error) {
      log_error(error);
    }
  }
</script>

<strong>
  {#if !is_account}
    {title}
  {:else}
    <AccountPageTitle account={title} />
    <button
      type="button"
      class="copy-account-title"
      title={copied ? "Copied" : "Copy account title"}
      aria-label={copied ? "Copied" : "Copy account title"}
      onclick={copyAccountTitle}
    >
      {#if copied}
        Copied
      {:else}
        ⧉
      {/if}
    </button>
  {/if}
</strong>

<style>
  strong::before {
    margin: 0 10px;
    font-weight: normal;
    content: "›";
    opacity: 0.5;
  }

  .copy-account-title {
    padding: 0 0.25rem;
    margin-left: 0.25rem;
    color: inherit;
    cursor: pointer;
    background: transparent;
    border: 0;
  }

  .copy-account-title:hover {
    color: var(--link-color);
  }
</style>
