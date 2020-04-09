import router from "./router";
import { notify } from "./notifications";
import { todayAsString } from "./format";
import { putAPI } from "./helpers";

interface Posting {
  account: string;
  amount: string;
}

interface Amount {
  number: string;
  currency: string;
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
    this.date = todayAsString();
  }
}

export class Balance extends Entry {
  account: string;

  amount: Amount;

  constructor() {
    super("Balance");
    this.account = "";
    this.amount = {
      number: "",
      currency: "",
    };
  }
}

export class Note extends Entry {
  account: string;

  comment: string;

  constructor() {
    super("Note");
    this.account = "";
    this.comment = "";
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

export async function saveEntries(entries: Entry[]): Promise<void> {
  if (!entries.length) {
    return;
  }
  try {
    const data = await putAPI("add_entries", { entries });
    router.reload();
    notify(data);
  } catch (error) {
    notify(`Saving failed: ${error}`, "error");
    throw error;
  }
}
