---
title: Beancount Syntax
---

# Beancount Language Syntax

Below is a short reference of the Beancount Language Syntax. For the official, full documentation see [furius.ca/beancount/doc/syntax](http://furius.ca/beancount/doc/syntax).

There is also an official [Syntax Cheat Sheet](http://furius.ca/beancount/doc/cheatsheet).

## Introduction

Beancount defines a language in which financial transactions are entered into a text-file (called input-file), which then can be processed by Beancount.

There are a few building blocks that are important to understand the entirety of the Beancount Languange Syntax:

- Currencies (`USD`, `EUR`, ...) and values
- Accounts (`Assets:US:BofA:Checking`, ...)
- Directives (`open`, `balance`, ...)
- Metadata


## Directives

The basic building block are **directives** (also called **entries**).

Each directive starts with a date, then the type of the directive, and then directive-specific arguments. The ordering of directives in the input-file does not matter, because Beancount orders them based on the date of each directive.

```beancount
; Directive syntax

YYYY-MM-DD <directive> <arguments...>

; Some example directives

2016-01-23 open Assets:US:BofA:Checking
2016-02-21 note Assets:US:BofA:Checking "Called to confirm wire transfer."
2016-02-10 balance Assets:US:BofA:Checking   154.20 USD
```

## Directive types

### `open` and `close`

To open or close an account use the `open` and `close` directives:

```beancount
2015-05-29 open Expenses:Restaurant
2015-05-29 open Assets:Checking     USD,EUR  ; Currency constraints
; ...
2016-02-23 close Assets:Checking
```









### `commodity`

```beancount
; This is optional; use this only if you want to attach metadata by currency.
1998-07-22 commodity AAPL
  name: "Apple Computer Inc."
```
