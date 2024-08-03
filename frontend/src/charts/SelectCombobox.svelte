<!--
  @component
  An element to select element(s) from a dropdown.

  It receives its `value` and a list of possible `options`. The `description` prop should
  render a human-readable string for the value (which will be displayed in the button) and
  option (which will be shown in the list popup). Optionally a `multiple_select` function
  can be passed and a selection of multiple options is possible for sets of options for
  which this returns true.

  This is an implementation of the Combobox pattern as described by the
  ARIA Authoring Practices Guide (APG) at
    https://www.w3.org/WAI/ARIA/apg/patterns/combobox/
  In particular it should match the Select-Only Combobox example at
    https://www.w3.org/WAI/ARIA/apg/patterns/combobox/examples/combobox-select-only/
-->
<script lang="ts" context="module">
  /** Incrementing number to use for element ids in the component. */
  let id = 0;
</script>

<script lang="ts">
  /** The currently entered value. */
  export let value: string;
  /** The options for the value. */
  export let options: readonly string[];
  /** Function to get the human readable description of an option and the value. */
  export let description: (option: string) => string;
  /** Whether an option can be part of a multi-selection (separated by comma in value). */
  export let multiple_select: ((option: string) => boolean) | undefined =
    undefined;

  /** Whether the list of options in the Combobox popup is hidden. */
  let hidden = true;
  /** The index of the option that is currently focused */
  let index = options.indexOf(value) ?? 0;
  /** The popup list element. */
  let ul: HTMLUListElement;

  id += 1;
  const listbox_id = `combobox-listbox-${id.toString()}`;

  const SEPARATOR = ",";
  $: values = value.split(SEPARATOR);

  // Scroll focused element into view.
  $: if (!hidden && index) {
    ul?.children[index]?.scrollIntoView({
      block: "nearest",
      inline: "nearest",
    });
  }

  /** The various actions that can be triggered by user mouse or key events. */
  const actions = {
    /** Close the popup list. */
    close: () => {
      hidden = true;
    },
    /** Find the first element matching the typed letter and focus it. */
    find_letter: (key: string, event: KeyboardEvent) => {
      const match = options.findIndex((o) => o.toLowerCase().startsWith(key));
      if (match > -1) {
        event.stopPropagation();
        index = match;
        hidden = false;
      }
    },
    /** Focus the first element and open if not open yet. */
    first: () => {
      index = 0;
      hidden = false;
    },
    /** Focus the last element and open if not open yet. */
    last: () => {
      index = 0;
      hidden = false;
    },
    /** Focus the previous element in the popup. */
    next: () => {
      index = index === 0 ? options.length - 1 : index - 1;
    },
    /** Open the popup list. */
    open: () => {
      hidden = false;
    },
    /** Focus the previous element in the popup. */
    previous: () => {
      index = index === options.length - 1 ? 0 : index + 1;
    },
    /** Select the given or the focused element in the options list. */
    select: (o?: string) => {
      const option = o ?? options[index];
      if (option != null) {
        if (
          multiple_select != null &&
          multiple_select(option) &&
          values.every(multiple_select)
        ) {
          value = values.includes(option)
            ? values.filter((v) => v !== option).join(SEPARATOR)
            : [...values, option].join(SEPARATOR);
        } else {
          value = option;
        }
        index = options.indexOf(option);
        hidden = true;
      }
    },
    /** Toggle the popup list. */
    toggle: () => {
      hidden = !hidden;
    },
  };

  /** Get the action for a keyboard event. */
  function key_action(event: KeyboardEvent): (() => void) | null {
    const { key } = event;
    const modifier = event.altKey || event.ctrlKey || event.metaKey;

    if (/^[\w]$/.exec(key) && !modifier) {
      return actions.find_letter.bind(null, key, event);
    }
    if (key === "Home") {
      return actions.first;
    }
    if (key === "End") {
      return actions.last;
    }
    if ((key === "Enter" || key === " ") && !hidden) {
      return actions.select;
    }
    if (key === "Escape" && !hidden) {
      return actions.close;
    }
    if (key === "ArrowUp") {
      return hidden ? actions.open : actions.next;
    }
    if (key === "ArrowDown") {
      return hidden ? actions.open : actions.previous;
    }
    return null;
  }
</script>

<span>
  <button
    type="button"
    role="combobox"
    aria-expanded={!hidden}
    aria-controls={listbox_id}
    class="muted"
    on:click={actions.toggle}
    on:blur={actions.close}
    on:keydown={(event) => {
      const action = key_action(event);
      if (action) {
        event.preventDefault();
        action();
      }
    }}
  >
    {description(value)}
  </button>
  <ul {hidden} role="listbox" id={listbox_id} bind:this={ul}>
    {#each options as option, i}
      <li
        role="option"
        aria-selected={values.includes(option)}
        class:current={i === index}
        on:mousedown={(ev) => {
          if (ev.button === 0) {
            actions.select(option);
          }
        }}
      >
        {description(option)}
      </li>
    {/each}
  </ul>
</span>

<style>
  span {
    position: relative;
    display: inline-block;
  }

  ul {
    position: absolute;
    z-index: var(--z-index-autocomplete);
    overflow: auto;
    background-color: var(--background);
    border: 1px solid var(--border-darker);
    box-shadow: var(--box-shadow-dropdown);
  }

  li {
    padding: 2px 5px;
    white-space: nowrap;
    cursor: pointer;
  }

  li.current {
    padding: 0 3px;
    border: var(--link-color) dotted 2px;
  }

  li[aria-selected="true"],
  li:hover {
    color: var(--background);
    background-color: var(--link-color);
  }

  @media print {
    span {
      display: none;
    }
  }
</style>
