Below is a short reference of the Beancount language syntax. Also see the full
[Syntax Documentation](http://furius.ca/beancount/doc/syntax) and the
[Syntax Cheat Sheet](http://furius.ca/beancount/doc/cheatsheet).

Beancount defines a language in which financial transactions are entered into a
text-file, which then can be processed by Beancount. There are a few building
blocks that are important to understand Beancount's syntax:

- Commodities,
- Accounts,
- Directives.

## Commodities

All in CAPS: `USD`, `EUR`, `CAD`, `GOOG`, `AAPL`, `RBF1005`, `HOME_MAYST`,
`AIRMILES`, `HOURS`.

## Accounts

Accounts are given by a colon-separated list of capitalized words. They must
begin with one of the five root accounts listed in the table below. The
separation by colons defines an implicit hierarchy, for example we say that
`Assets:Cash` is a sub-account of `Assets`.

| Name          | Type | Contains                     | Examples                  |
| ------------- | ---- | ---------------------------- | ------------------------- |
| `Assets`      | +    | Cash, Checking-Account, etc. | `Assets:Checking`         |
| `Liabilities` | -    | Credit Card, etc.            | `Liabilities:CreditCard`  |
| `Income`      | -    | Salary, etc.                 | `Income:EmployerA`        |
| `Expenses`    | +    | Expense categories           | `Expenses:Fun:Cinema`     |
| `Equity`      | -    | Almost always auto-generated | `Equity:Opening-Balances` |

The names of the five root accounts can be changed with the following options:

```beancount
option "name_assets"      "Vermoegen"
option "name_liabilities" "Verbindlichkeiten"
option "name_income"      "Einkommen"
option "name_expenses"    "Ausgaben"
option "name_equity"      "Eigenkapital"
```

## Directives

The basic building block are **directives** (also called **entries**). Most
directives start with a date, then the type of the directive, and then
directive-specific arguments. The ordering of directives in the input-file does
not matter, because Beancount orders them based on the date of each directive.

General syntax: `YYYY-MM-DD <directive> <arguments...>`

### Open and Close accounts

To open or close an account use the `open` and `close` directives:

```beancount
2015-05-29 open Expenses:Restaurant
; Account with some currency constraints:
2015-05-29 open Assets:Checking     USD,EUR
; ...
2016-02-23 close Assets:Checking
```

### Commodity directives

Declaring commodities is optional. Use this if you want to attach metadata by
currency. If you specify a `name` for a currency like below, this name will be
displayed as a tooltip on hovering over currency names in Fava. Likewise, with
the `precision` metadata, you can specify the number of decimal digits to show
in Fava, overriding the precision that is otherwise automatically inferred from
the input data.

```beancount
1998-07-22 commodity AAPL
  name: "Apple Computer Inc."
  precision: 3
```

### Prices

You can use this directive to fill the historical price database:

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

2015-05-30 ! "Cable Co" "Phone Bill" #tag ^link
  id: "TW378743437"
  Expenses:Home:Phone  87.45 USD
  Assets:Checking                 ; You may leave one amount out
```

### Postings

```beancount
2015-05-30 * "Example transaction with various postings"
  Account:Name   123.45 USD                           ; simple units
  Account:Name      10 GOOG {502.12 USD}              ; with cost
  Account:Name  1000.00 USD  @ 1.10 CAD               ; with price
  Account:Name      10 GOOG {502.12 USD} @ 1.10 CAD   ; with cost & price
  Account:Name      10 GOOG {502.12 USD, 2014-05-12}  ; with cost date
  ! Account:Name 123.45 USD                           ; with flag
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
; ... the given tag will be added to all entries in between the pushtag and poptag
poptag  #trip-to-peru
```

### Comments

```beancount
; inline comments begin with a semi-colon
* any line not starting with a valid directive is also ignored silently
```
