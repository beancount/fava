# Budgets

Budgets on a per-account basis can be added via `custom` directives in the
Beancount file:

<pre><textarea is="beancount-textarea">
2012-01-01 custom "budget" Expenses:Coffee       "daily"         4.00 EUR
2013-01-01 custom "budget" Expenses:Books        "weekly"       20.00 EUR
2013-01-01 custom "budget" Expenses:Fuel         "fortnightly"  60.00 EUR
2014-02-10 custom "budget" Expenses:Groceries    "monthly"      40.00 EUR
2015-05-01 custom "budget" Expenses:Electricity  "quarterly"    85.00 EUR
2016-06-01 custom "budget" Expenses:Holiday      "yearly"     2500.00 EUR</textarea></pre>

If budgets are specified, Fava's reports and charts will display remaining
budgets and related information.

Each budget directive has an accunt for which the budget is specified, a
frequency and amount of the budget, and a date from which the budget is valid. A
budget directive remains valid until another budget directive for the account is
specified. For example:

<pre><textarea is="beancount-textarea">
2012-01-01 custom "budget" Expenses:Coffee       "daily"         4.00 EUR
2013-01-01 custom "budget" Expenses:Coffee       "daily"         5.00 EUR
2014-01-01 custom "budget" Expenses:Coffee       "weekly"        6.00 EUR</textarea></pre>

In this example, the coffee budget is 4.00 EUR for 2012, then increases to 5.00
EUR in 2013, and finally to 30 EUR per week in 2014.

Fava supports the following frequencies for the budget:

- `daily`
- `weekly`
  - The week align with ISO weeks, and start on Monday.
- `fortnightly`
  - Note that there are no standard conventions for dividing a year into
    fortnights, and as such, Fava uses the following:
    - The fortnight align with ISO weeks, with the first fortnight being W01 and
      W02 of the year.
    - For a year with 53 weeks, the last fortnight is W53 and W54 (equivalent to
      the next year's W01). This unfortunately does result in overlapping
      fortnights once every 7 years approximately.
- `monthly`
  - This is the calendar month, and Fava internally uses the number of days in
    each month to calculate the monthly budget. As a result, February with 28
    days will have a lower budget than January with 31 days.
- `quarterly`
  - Based on the calendar quarter, with the quarters starting on January 1,
    April 1, July 1, and October 1.
- `yearly`

Fava displays budgets in both charts and reports. You can find a visualization
of the global budget in the `Net Profit` and `Expenses` charts for the Income
Statement report.

The Income Statement report is a good starting point for getting access to the
full budget information in Fava. The `Changes` charts visualize the data. The
`Changes (monthly)` and `Balances (monthly)` reports show, respectively, the
monthly and cumulative (over the selected period) budgets.
