<script lang="ts">
  export let value: string;
  export let options: [string, string][];
</script>

<span>
  {#each options as [option, name]}
    <label class="button" class:muted={value !== option}>
      <input type="radio" bind:group={value} value={option} />
      {name}
    </label>
  {/each}
</span>

<style>
  input {
    display: none;
  }

  label + label {
    margin-left: 0.25rem;
  }
</style>
