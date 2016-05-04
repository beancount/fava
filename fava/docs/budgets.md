---
title: Budgets
---

# Budgeting

Budgets on an per-account basis can be added via `custom` directives in the
beancount-file:

    2012-01-01 custom "budget" Expenses:Coffee             "daily"         4.00 EUR
    2013-01-01 custom "budget" Expenses:Books              "weekly"       20.00 EUR
    2014-02-10 custom "budget" Expenses:Groceries          "monthly"      40.00 EUR
    2015-05-01 custom "budget" Expenses:House:Electricity  "quarterly"    85.00 EUR
    2016-06-01 custom "budget" Expenses:Holiday            "yearly"     2500.00 EUR

If budgets are specified, treetables and charts will display remaining budgets
and other budgeting-related information. 

The budget-directives can be specified `daily`, `weekly`, `monthly`, `quarterly`
and `yearly`. The specified budget is valid until the next budget-directive is 
found (date-sorted). The budget is always calculated with the currently active
budget-directive, broken down to a daily budget, and summed up for the specified
date-range.

This makes the budget-directives very flexible, allowing for a monthly budget, 
being taken over by a weekly budget, and so on. 
