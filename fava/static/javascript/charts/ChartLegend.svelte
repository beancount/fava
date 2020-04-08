<script>
  export let legend;
</script>

<style>
  p {
    flex-grow: 1;
  }

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

<p>
  {#each legend as [item, color]}
    <span>
      <i style="background-color: {color}" />
      {item}
    </span>
  {/each}
</p>
