---
title: Syntax Cheat Sheet
---

# Beancount Language Syntax Cheat Sheet

This is a copy of the official [Syntax Cheat
Sheet](http://furius.ca/beancount/doc/cheatsheet) by Martin Blais.

## Commodities

All in CAPS: `USD`, `EUR`, `CAD`, `AUD` `GOOG`, `AAPL`, `RBF1005` `HOME_MAYST`,
`AIRMILES` `HOURS`

## Account Types

Example Account Name: `Assets:US:BofA:Checking`

| Name          | Type | Contains                     | Examples                        | Option to change name                           |
|---------------|------|------------------------------|---------------------------------|-------------------------------------------------|
| `Assets`      | +    | Cash, Checking-Account, etc. | `Assets:Checking`         | `option "name_assets" "Vermoegen"`              |
| `Liabilities` | -    | Credit Card, etc.            | `Liabilities:CreditCard`  | `option "name_liabilities" "Verbindlichkeiten"` |
| `Income`      | -    | Salary, etc.                 | `Income:EmployerA`        | `option "name_income" "Einkommen"`              |
| `Expenses`    | +    | Expense-Categories           | `Expenses:Fun:Cinema`     | `option "name_expenses" "Ausgaben"`             |
| `Equity`      | -    | Almost always auto-generated | `Equity:Opening-Balances` | `option "name_equity" "Eigenkapital"`           |

## Directives

General syntax: `YYYY-MM-DD <directive> <arguments...>`

### Opening & Closing Accounts

```beancount
2001-05-29 open Expenses:Restaurant
2001-05-29 open Assets:Checking     USD,EUR  ; Currency constraints

2015-04-23 close Assets:Checking
```

### Declaring Commodities

This is optional; use this only if you want to attach metadata by currency.

```beancount
1998-07-22 commodity AAPL
  name: "Apple Computer Inc."
```

### Prices

Use many times to fill historical price database:

```beancount
2015-04-30 price AAPL   125.15 USD
2015-05-30 price AAPL   130.28 USD
```

### Notes

```beancount
2013-03-20 note Assets:Checking "Called to ask about rebate"
```

### Documents

```beancount
2013-03-20 document Assets:Checking "path/to/statement.pdf"
```

### Transactions

```beancount
2015-05-30 * "Some narration about this transaction"
  Liabilities:CreditCard   -101.23 USD
  Expenses:Restaurant       101.23 USD

2015-05-30 ! "Cable Co" "Phone Bill" #tag ˆlink
  id: "TW378743437"               ; Meta-data
  Expenses:Home:Phone  87.45 USD
  Assets:Checking                 ; You may leave one amount out
```

### Postings

```beancount
...    123.45 USD                             ; simple
...        10 GOOG {502.12 USD}               ; with cost
...   1000.00 USD   @ 1.10 CAD                ; with price
...        10 GOOG {502.12 USD} @ 1.10 CAD    ; with cost & price
...        10 GOOG {502.12 USD / 2014-05-12}  ; with date
! ...   123.45 USD ...                        ; with flag
```

### Balance Assertions and Padding

Asserts the amount for only the given currency:

```beancount
2015-06-01 balance Liabilities:CreditCard  -634.30 USD
```

Automatic insertion of transaction to fulfill the following assertion:

```beancount
2015-06-01 pad Assets:Checking Equity:Opening-Balances
```

### Events

```beancount
2015-06-01 event "location" "New York, USA"
2015-06-01 event "address" "123 May Street"
```

### Options

See the [Beancount Options Reference](http://furius.ca/beancount/doc/options)
for the full list of supported options.

```beancount
option "title" "My Personal Ledger"
```

### Other

```beancount
pushtag #trip-to-peru
...
poptag  #trip-to-peru
```

```beancount
; Comments begin with a semi-colon
```
