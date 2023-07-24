export default {
  async runQuery() {
    const queryStr = document.getElementById("batch_edit_query").value;
    console.log(queryStr);
    if (!queryStr) {
      return;
    }
    let searchParams = new URLSearchParams(window.location.search);
    searchParams.set("query", queryStr);
    window.location.search = searchParams.toString();
    return;
  },
  onExtensionPageLoad() {
    const submitQuery = document.getElementById("batch_query_submit");
    submitQuery.addEventListener("click", () => {
      this.runQuery();
    });
  },
};
