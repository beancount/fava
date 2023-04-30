export default {
  onExtensionInit() {},
  onExtensionPageLoad() {},
  updateFilter() {
    const filterInput = document.getElementById("portfolio-list-filter");
    if (filterInput.value.length) {
      const search = new URLSearchParams(window.location.search);
      search.set("account_filter", filterInput.value);
      window.location.search = search.toString();
    }
  },
  clearFilter() {
    const search = new URLSearchParams(window.location.search);
    search.delete("account_filter");
    window.location.search = search.toString();
  },
};
