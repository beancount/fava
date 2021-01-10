<script>
  /** @type {[string, string][]} */
  export let legend;
</script>

{#each legend as [item, color]}
  <span> <i style="background-color: {color}" /> {item} </span>
{/each}

<style>
  span,
  i {
    display: inline-block;
  }

  i {
    width: 10px;
    height: 10px;
    margin-left: 5px;
    border-radius: 10px;
  }
</style>
