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

abstract class Entry {
  type: string;

  date: string;

  meta: Record<string, string>;

  constructor(type: string) {
    this.type = type;
    this.meta = {};
    this.date = new Date().toISOString().slice(0, 10);
  }
}

export class Balance extends Entry {
  account: string;

  constructor() {
    super("Balance");
    this.account = "";
  }
}

export class Transaction extends Entry {
  flag: string;

  payee: string;

  narration: string;

  postings: Posting[];

  constructor() {
    super("Transaction");
    this.flag = "*";
    this.payee = "";
    this.narration = "";
    this.postings = [new Posting(), new Posting()];
  }
}

export async function saveEntries(entries: Entry[]) {
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
