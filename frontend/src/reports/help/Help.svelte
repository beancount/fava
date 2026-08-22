<script lang="ts">
  import { url_for } from "../../helpers.ts";
  import { _ } from "../../i18n.ts";
  import type { HelpReportProps } from "./index.ts";

  let { page_slug, html, pages }: HelpReportProps = $props();
</script>

<div class="help">
  <nav class="help-sidebar">
    <h3>{_("Help pages")}</h3>
    <ul>
      {#each pages as [slug, title] (slug)}
        <li>
          <a
            href={$url_for(slug === "_index" ? "help/" : `help/${slug}`)}
            class:selected={slug === page_slug}
          >
            {title}
          </a>
        </li>
      {/each}
    </ul>
  </nav>
  <div class="help-text">
    <!-- eslint-disable-next-line svelte/no-at-html-tags -->
    {@html html}
  </div>
</div>

<style>
  .help {
    --help-max-width: 700px;

    max-width: calc(var(--help-max-width) + 160px);
    font-size: 16px;
  }

  nav {
    float: right;
    padding: 1rem 1rem 0;
    margin: 0 0 1rem 1rem;
    background-color: var(--sidebar-background);
    border: 1px solid var(--sidebar-border);

    a:hover,
    a.selected {
      font-weight: 500;
    }
  }

  .help-text {
    max-width: var(--help-max-width);

    :global(code),
    :global(.cm-editor) {
      font-size: 14px;
    }

    :global(ul) {
      padding-left: 2em;

      li {
        list-style-type: disc;
      }
    }
  }
</style>
