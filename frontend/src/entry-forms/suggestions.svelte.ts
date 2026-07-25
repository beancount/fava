import { get_narrations, get_payee_accounts } from "../api/index.ts";
import { notify_err } from "../notifications.ts";

interface FetchData<T> {
  /** The currently fetched data - a reactive property. */
  data: Readonly<T> | undefined;
}

/**
 * Ensure a data fetching operation runs only once.
 *
 * Keeps track of the ledger mtime when loaded and will load again when that changes.
 */
class FetchCoalescer<T> implements FetchData<T> {
  data = $state.raw<Readonly<T>>();

  #loader: () => Promise<T>;
  #error_msg: (error: Error) => string;

  #mtime: bigint | null = null;
  #inflight: Promise<void> | null = null;

  constructor(loader: () => Promise<T>, error_msg: (error: Error) => string) {
    this.#loader = loader;
    this.#error_msg = error_msg;
  }

  /** Fetch the data, reusing cached data or a parallel fetch operation that is in flight. */
  load(mtime: bigint): this {
    if (this.data != null && this.#mtime === mtime) {
      return this;
    }
    if (this.#inflight) {
      return this;
    }
    this.#inflight = this.#loader()
      .then((data) => {
        this.data = data;
        this.#mtime = mtime;
        this.#inflight = null;
      })
      .catch((error: unknown) => {
        notify_err(error, (err) => this.#error_msg(err));
        this.#inflight = null;
      });
    return this;
  }
}

const narrations = new FetchCoalescer(
  get_narrations,
  (err) => `Fetching narration suggestions failed: ${err.message}`,
);

export function fetch_narrations(mtime: bigint): FetchData<string[]> {
  return narrations.load(mtime);
}

// eslint-disable-next-line svelte/prefer-svelte-reactivity
const payee_accounts = new Map<string, FetchCoalescer<string[]>>();

export function fetch_payee_accounts(
  mtime: bigint,
  payee: string,
): FetchData<string[]> {
  let fetcher = payee_accounts.get(payee);
  if (fetcher == null) {
    fetcher = new FetchCoalescer(
      async () => get_payee_accounts({ payee }),
      (err) =>
        `Fetching account suggestions for payee '${payee}' failed: ${err.message}`,
    );
    payee_accounts.set(payee, fetcher);
  }
  return fetcher.load(mtime);
}
