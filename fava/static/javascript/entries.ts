import router from "./router";
import { notify } from "./notifications";
import { putAPI } from "./helpers";

interface Posting {
  account: string;
  amount: string;
}

export function emptyPosting(): Posting {
  return {
    account: "",
    amount: "",
  };
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
    this.postings = [emptyPosting(), emptyPosting()];
  }
}

export async function saveEntries(entries: Entry[]) {
  if (!entries.length) return;
  try {
    const data = await putAPI("add_entries", { entries });
    router.reload();
    notify(data);
  } catch (error) {
    notify(`Saving failed: ${error}`, "error");
    throw error;
  }
}
