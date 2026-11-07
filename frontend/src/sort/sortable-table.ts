import { get_direction, sort_elements } from "./index.ts";

export class SortableTable extends HTMLElement {
  constructor() {
    super();
    const table = this.querySelector("table");
    const head = table?.tHead;
    const body = table?.tBodies.item(0);
    if (!head || !body) {
      return;
    }
    const headers = [...head.querySelectorAll("th[data-sort]")];

    headers.forEach((header, index) => {
      header.addEventListener("click", () => {
        const order =
          header.getAttribute("data-order") === "asc" ? "desc" : "asc";
        const type = header.getAttribute("data-sort");

        // update sort order
        headers.forEach((e) => {
          e.removeAttribute("data-order");
        });
        header.setAttribute("data-order", order);

        sort_elements<HTMLTableRowElement>(
          body,
          [...body.querySelectorAll("tr")],
          (tr) => tr.cells.item(index),
          get_direction(order),
          type,
        );
      });
    });
  }
}
