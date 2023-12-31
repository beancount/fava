# Budgets

Budgets on a per-account basis can be added via `custom` directives in the
Beancount file:

<pre><textarea is="beancount-textarea">
2012-01-01 custom "budget" Expenses:Coffee       "daily"         4.00 EUR
2013-01-01 custom "budget" Expenses:Books        "weekly"       20.00 EUR
2014-02-10 custom "budget" Expenses:Groceries    "monthly"      40.00 EUR
2015-05-01 custom "budget" Expenses:Electricity  "quarterly"    85.00 EUR
2016-06-01 custom "budget" Expenses:Holiday      "yearly"     2500.00 EUR</textarea></pre>

If budgets are specified, Fava's reports and charts will display remaining
budgets and related information.

The budget directives can be specified `daily`, `weekly`, `monthly`, `quarterly`
and `yearly`. The specified budget is valid until another budget directive for
the account is specified. The budget is broken down to a daily budget, and
summed up for a range of dates as needed.

This makes the budgets very flexible, allowing for a monthly budget, being taken
over by a weekly budget, and so on.

Fava displays budgets in both charts and reports. You can find a visualization
of the global budget in the `Net Profit` and `Expenses` charts for the Income
Statement report.

The Income Statement report is a good starting point for getting access to the
full budget information in Fava. The `Changes` charts visualize the data. The
`Changes (monthly)` and `Balances (monthly)` reports show, respectively, the
monthly and cumulative (over the selected period) budgets.
