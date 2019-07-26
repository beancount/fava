import router from "./router";
import { notify } from "./notifications";
import { fetch, handleJSON } from "./helpers";
import { favaAPI } from "./stores";

export class Posting {
  account: string;

  amount: string;

  constructor() {
    this.account = "";
    this.amount = "";
  }
}

export class Transaction {
  constructor() {
    Object.assign(this, {
      type: "Transaction",
      date: new Date().toISOString().slice(0, 10),
      flag: "*",
      payee: "",
      narration: "",
      meta: {},
      postings: [new Posting(), new Posting()],
    });
  }
}

export async function saveEntries(entries) {
  if (!entries.length) return;
  try {
    const data = await fetch(`${favaAPI.baseURL}api/add-entries/`, {
      method: "PUT",
      body: JSON.stringify({ entries }),
      headers: { "Content-Type": "application/json" },
    }).then(handleJSON);
    router.reload();
    notify(data.message);
  } catch (error) {
    notify(`Saving failed: ${error}`, "error");
    throw error;
  }
}
