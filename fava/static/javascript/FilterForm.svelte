<script>
  import { _ } from "./helpers";
  import { filters as filterStore } from "./stores";

  const filters = [
    {
      name: "time",
      placeholder: _("Time"),
      key: "f t",
      list: "years",
    },
    {
      name: "account",
      placeholder: _("Account"),
      key: "f a",
      list: "accounts",
    },
    {
      name: "filter",
      placeholder: _("Filter by tag, payee, ..."),
      key: "f f",
      list: "tags",
    },
  ];

  let values;
  filterStore.subscribe(fs => {
    values = Object.assign({}, fs);
  });

  function submit() {
    filterStore.update(fs => {
      Object.assign(fs, values);
      return fs;
    });
  }

  function clear(name) {
    filterStore.update(fs => {
      fs[name] = "";
      return fs;
    });
  }
</script>

<form id="filter-form" class="filter-form" on:submit|preventDefault={submit}>
  {#each filters as { name, placeholder, key, list }}
    <span class:empty={!values[name]}>
      <input
        data-key={key}
        {name}
        type="text"
        bind:value={values[name]}
        {placeholder}
        {list}
        on:autocomplete-select={submit}
        size={Math.max(values[name].length, placeholder.length) + 1} />
      <button
        type="button"
        tabindex="-1"
        class="close muted round"
        on:click={() => clear(name)}>
        ×
      </button>
    </span>
  {/each}
  <button type="submit" />
</form>
