// @ts-check

/** @type import("../../../../frontend/src/extension-api").ExtensionModule */
export default {
  init() {
    console.log("initialising Javascript extension PortfolioList");
  },
  onPageLoad() {
    console.log("A Fava report page has loaded", window.location.pathname);
  },
  onExtensionPageLoad() {
    console.log(
      "The page for the PortfolioList extension has loaded",
      window.location.pathname,
    );

    const updateFilter = document.getElementById("portfolio-update-filter");
    updateFilter?.addEventListener("click", () => {
      const filterInput = document.getElementById("portfolio-list-filter");
      if (filterInput instanceof HTMLInputElement && filterInput.value.length) {
        const search = new URLSearchParams(window.location.search);
        search.set("account_filter", filterInput.value);
        window.location.search = search.toString();
      }
    });

    const clearFilter = document.getElementById("portfolio-clear-filter");
    clearFilter?.addEventListener("click", () => {
      const search = new URLSearchParams(window.location.search);
      search.delete("account_filter");
      window.location.search = search.toString();
    });
  },
};
