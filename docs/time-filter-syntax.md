# Fava Time Filter Syntax

The Time search box at the top of the Fava UI accepts a custom date expression language. The input is sent as the `?time=` URL parameter and parsed server-side by `parse_date()` in `src/fava/util/date.py`.

## How it works

1. The frontend (`FilterForm.svelte`) sends the raw string as the `time` query parameter.
2. The backend (`TimeFilter` in `filters.py`) calls `parse_date(value, fiscal_year_end)`.
3. If parsing returns `(None, None)`, a `TimeFilterParseError` is raised and shown to the user.
4. Otherwise, the returned `(begin, end)` tuple is used to clamp entries via `clamp_opt()`.

All dates are **inclusive on the start, exclusive on the end**. A range `2024` means Jan 1, 2024 through Jan 1, 2025 (all of 2024).

---

## 1. Single-date formats

| Format | Example | Start | End | Notes |
|---|---|---|---|---|
| `YYYY` | `2024` | 2024-01-01 | 2025-01-01 | Full calendar year |
| `YYYY-MM` | `2024-03` | 2024-03-01 | 2024-04-01 | Calendar month |
| `YYYY-MM-DD` | `2024-03-15` | 2024-03-15 | 2024-03-16 | Single day |
| `YYYY-Www` | `2024-W03` | 2024-01-15 | 2024-01-22 | ISO week (Monday start) |
| `YYYY-Qn` | `2024-Q1` | 2024-01-01 | 2024-04-01 | Calendar quarter (Q1-Q4) |
| `FYYYYY` | `FY2024` | 2023-07-01 | 2024-07-01 | Fiscal year (depends on `fiscal-year-end` option; shown with FYE=06-30) |
| `FYYYYY-Qn` | `FY2024-Q2` | 2023-10-01 | 2024-01-01 | Fiscal quarter (depends on `fiscal-year-end`; FYE must start on 1st of a month) |

---

## 2. Range formats

Two dates separated by ` - ` or ` to `:

| Example | Start | End |
|---|---|---|
| `2024 - 2025` | 2024-01-01 | 2026-01-01 |
| `2024 to 2025` | 2024-01-01 | 2026-01-01 |
| `2024-03 - 2025` | 2024-03-01 | 2026-01-01 |
| `2024-01-15 - 2024-03` | 2024-01-15 | 2024-04-01 |
| `FY2019 - FY2020` | 2018-07-01 | 2020-07-01 |
| `FY2019 - 2020` | 2018-07-01 | 2021-01-01 |
| `2011 to FY2015` | 2011-01-01 | 2015-07-01 |

Each side of the range can be any single-date format. The range regex matches `-` or `to` only when followed by whitespace and a year-like pattern (`fyYYYY` or `YYYY`).

---

## 3. Relative keywords

These resolve against **today's date**. They can appear anywhere a date is expected (single or range).

| Keyword | Today=2016-06-24 | Start | End |
|---|---|---|---|
| `year` | 2016 | 2016-01-01 | 2017-01-01 |
| `year-1` | 2015 | 2015-01-01 | 2016-01-01 |
| `year+3` | 2019 | 2019-01-01 | 2020-01-01 |
| `month` | 2016-06 | 2016-06-01 | 2016-07-01 |
| `month-1` | 2016-05 | 2016-05-01 | 2016-06-01 |
| `month+6` | 2016-12 | 2016-12-01 | 2017-01-01 |
| `quarter` | 2016-Q2 | 2016-04-01 | 2016-07-01 |
| `quarter+2` | 2016-Q4 | 2016-10-01 | 2017-01-01 |
| `week` | 2016-W25 | 2016-06-20 | 2016-06-27 |
| `week+20` | 2016-W45 | 2016-11-07 | 2016-11-14 |
| `day` | 2016-06-24 | 2016-06-24 | 2016-06-25 |
| `day+20` | 2016-07-14 | 2016-07-14 | 2016-07-15 |
| `fiscal_year` | FY2018 | 2017-07-01 | 2018-07-01 |
| `fiscal_year-1` | FY2017 | 2016-07-01 | 2017-07-01 |
| `fiscal_quarter` | FY2018-Q3 | 2018-01-01 | 2018-04-01 |

Keywords can be **parenthesized**: `(year)`, `(year+3)`. Parentheses are optional but can help disambiguate in ranges.

### Fiscal year details

`fiscal_year` and `fiscal_quarter` depend on the `fiscal-year-end` option (format `MM-DD`, default `12-31`). The offset from the end of the fiscal year determines which FY label applies:

- With FYE=06-30: a date in Feb 2018 is in FY2018 (before June 30); a date in Aug 2018 is in FY2019 (after July 1).
- With FYE=04-05 (UK-style): a date in Feb 2018 is in FY2017; a date in May 2018 is in FY2018.
- With FYE=15-31 (offset fiscal year, e.g. Japan): month 15 = March of the next calendar year.

Fiscal quarters are only available when the fiscal year starts on the first of a month (e.g. FYE=06-30 works; FYE=04-05 does not).

---

## 4. Relative ranges

Both sides of a range can use relative keywords:

| Example (today=2016-06-24, FYE=06-30) | Start | End |
|---|---|---|
| `year-2 - day+2` | 2014-01-01 | 2016-06-27 |
| `year - day` | 2016-01-01 | 2016-06-25 |
| `2015 - year` | 2015-01-01 | 2017-01-01 |
| `quarter-1` | 2016-01-01 | 2016-04-01 |
| `fiscal_year-2` | 2013-07-01 | 2014-07-01 |

---

## 5. Date-math syntax (Elasticsearch/Grafana style)

Fava supports the Elasticsearch/Grafana date-math syntax:

```
now[+/-Nunit][/snap]
```

This is resolved against today's date.

### Units

| Unit | Meaning | Example |
|---|---|---|
| `d` | Days | `now-30d` = 30 days ago |
| `w` | Weeks | `now-1w` = 1 week ago |
| `M` | Months | `now-1M` = 1 month ago |
| `y` | Years | `now-1y` = 1 year ago |

### Snaps: what they are and why they matter

A **snap** rounds a date down to the start of a period. This is the key concept that makes date-math useful for financial reporting.

Without a snap, `now-1y` means "exactly 1 year ago" -- a single point in time (2025-07-26). That's rarely what you want in a ledger. With a snap, `now-1y/y` means "the start of the year that was 1 year ago" (2025-01-01), giving you the full calendar year.

The snap is applied **after** the offset. So `now-1y/y` is: take today, subtract 1 year, then snap to the start of that year.

| Snap | Rounds down to | Example |
|---|---|---|
| `/d` | Start of day (identity for date-only) | `now/d` = today at midnight |
| `/w` | Monday of the week | `now/w` = this Monday |
| `/M` | First of the month | `now/M` = first of this month |
| `/y` | First of the year | `now/y` = first of this year |
| `/fy` | Start of the fiscal year | `now/fy` = start of current fiscal year |
| `/fQ` | Start of the fiscal quarter | `now/fQ` = start of current fiscal quarter |

**Without an explicit snap, the unit determines the period.** For example, `now-1M` is equivalent to `now-1M/M` -- it snaps to the month boundary automatically. This matches the intuitive reading: "last month" means the calendar month, not a single day 30 days ago.

### Examples (today=2026-07-26)

| Expression | Start | End | Meaning |
|---|---|---|---|
| `now` | 2026-07-26 | 2026-07-27 | Today |
| `now-1d` | 2026-07-25 | 2026-07-26 | Yesterday |
| `now-7d` | 2026-07-19 | 2026-07-20 | 7 days ago |
| `now-1w` | 2026-07-13 | 2026-07-20 | Last week (Mon-Mon) |
| `now-1M` | 2026-06-01 | 2026-07-01 | Last month |
| `now-1y` | 2025-01-01 | 2026-01-01 | Last calendar year |
| `now+1M` | 2026-08-01 | 2026-09-01 | Next month |
| `now/d` | 2026-07-26 | 2026-07-27 | Start of today |
| `now/M` | 2026-07-01 | 2026-08-01 | This month |
| `now/y` | 2026-01-01 | 2027-01-01 | This year |
| `now-1y/y` | 2025-01-01 | 2026-01-01 | Last calendar year (explicit snap) |
| `now-1M/M` | 2026-06-01 | 2026-07-01 | Last month (explicit snap) |
| `now-1d/d` | 2026-07-25 | 2026-07-26 | Yesterday (explicit snap) |
| `now/w` | 2026-07-20 | 2026-07-27 | This week |
| `now-1w/w` | 2026-07-13 | 2026-07-20 | Last week (explicit snap) |

### Fiscal snaps (FYE=06-30)

| Expression | Start | End | Meaning |
|---|---|---|---|
| `now/fy` | 2026-07-01 | 2027-07-01 | Current fiscal year |
| `now-1y/fy` | 2025-07-01 | 2026-07-01 | Last fiscal year |
| `now/fQ` | 2026-07-01 | 2026-10-01 | Current fiscal quarter |

### Date-math ranges

| Expression | Start | End | Meaning |
|---|---|---|---|
| `now-30d - now` | 2026-06-26 | 2026-07-26 | Last 30 days |
| `now-1y - now` | 2025-07-26 | 2026-07-26 | Last 365 days |
| `now/M - now` | 2026-07-01 | 2026-07-26 | Month to date |
| `now-1y/y - now/y` | 2025-01-01 | 2026-01-01 | Last calendar year (range form) |
| `now-7d - now-1d` | 2026-07-19 | 2026-07-25 | 7 days ago through yesterday |

### How snaps work step by step

`now-1y/y` with today=2026-07-26:

1. Start with `now` = 2026-07-26
2. Apply offset `-1y` = 2025-07-26
3. Apply snap `/y` = round down to start of year = 2025-01-01
4. End = start of next year = 2026-01-01
5. Result: 2025-01-01 to 2026-01-01 (all of 2025)

`now-1y` (no explicit snap, unit=y implies snap to year):

1. Start with `now` = 2026-07-26
2. Apply offset `-1y` = 2025-07-26
3. Implicit snap to year = 2025-01-01
4. End = start of next year = 2026-01-01
5. Result: 2025-01-01 to 2026-01-01 (same as `now-1y/y`)

`now-30d - now` (range, no snap on either side):

1. Left: `now-30d` = 2026-06-26 (no snap, just offset)
2. Right: `now` = 2026-07-26 (no snap)
3. Result: 2026-06-26 to 2026-07-26 (rolling 30-day window)

---

## 6. Edge cases

| Input | Result |
|---|---|
| Empty or whitespace-only | `(None, None)` -- no filter applied |
| `   2000   ` | Whitespace is stripped; parses as year 2000 |
| Unparseable string (e.g. `abc`) | `(None, None)` -- raises `TimeFilterParseError` |

---

## 7. Implementation reference

- **Frontend input**: `frontend/src/sidebar/FilterForm.svelte` -- `AutocompleteInput` with `suggestions={$years}`
- **Brush widget**: `frontend/src/charts/Brush.svelte` -- drag-select sets `time` param as `"start - end"`
- **URL store**: `frontend/src/stores/filters.ts` -- reads `?time=` from URL
- **Date format for brush output**: `frontend/src/format.ts` -- `timeFilterDateFormat` maps interval to format string
- **Backend parser**: `src/fava/util/date.py` -- `parse_date()`, `substitute()`, `_parse_datemath()`
- **Filter application**: `src/fava/core/filters.py` -- `TimeFilter` class
- **Tests**: `tests/test_util_date.py` -- comprehensive parametrized test suite
