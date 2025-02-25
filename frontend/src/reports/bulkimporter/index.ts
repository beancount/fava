import { Transaction } from "../../entries";
import type { Entry } from "../../entries";

function negate_amount(amount: string) {
    if (amount.trimStart().startsWith("-")) {
        return amount.trimStart().slice(1);
    } else {
        return "-" + amount;
    }
}

// Wrapper around Transaction.
export class SimpleTransaction {
    // The original transaction. This is guaranteed to have exactly 2
    // postings (checked in the constructor).
    transaction: Transaction;
    readonly origin_account: string;
    readonly target_posting_index: number;
    readonly origin_posting_index: number;
    // Remember the index in the upstream list of `SimpleTransaction`s.  Because
    // of Svelte's reactivity, we have to maintain paralell data structures to
    // track local edits that are not purely functional (as otherwise, the changes
    // get overwritten any time Svelte recomputes derived values).
    readonly index: number;

    constructor(transaction: Transaction, origin_account: string, index: number) {
        this.transaction = transaction;
        this.origin_account = origin_account;
        this.index = index;

        let target_postings = this.transaction.postings
            .map((posting, index) => ({ posting: posting, index: index }))
            .filter(({ posting, }) => !posting.is_empty() && posting.account !== this.origin_account);
        if (this.transaction.postings.length !== 2) {
            throw new Error("A transaction with more than 2 postings is not a 'simple' transaction.")
        }
        if (target_postings.length !== 1) {
            throw new Error("Expected exactly one posting whose account was not" +
                this.origin_account + ", but found " +
                JSON.stringify(target_postings))
        } else {
            this.target_posting_index = target_postings[0]!.index;
            this.origin_posting_index = 1 - this.target_posting_index;
        }
    }

    getTargetAccount() {
        return this.transaction.postings[this.target_posting_index]!.account;
    }

    setTargetAccount(target: string) {
        this.transaction.postings[this.target_posting_index]!.account = target;
    }

    getAmount() {
        return this.transaction.postings[this.origin_posting_index]!.amount || negate_amount(this.transaction.postings[this.target_posting_index]!.amount)
    }
}