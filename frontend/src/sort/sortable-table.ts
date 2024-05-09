import { get_direction, sortElements } from ".";

export class SortableTable extends HTMLTableElement {
  constructor() {
    super();
    const body = this.tBodies.item(0);
    if (!this.tHead || !body) {
      return;
    }
    const headers = [...this.tHead.querySelectorAll("th[data-sort]")];

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

        sortElements<HTMLTableRowElement>(
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
