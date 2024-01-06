# Conversion

In most reports in Fava, a conversion can be selected with the select dropdown
at the top of the chart. These conversions will use the prices defined in the
Beancount file, so these should defined manually or by some plugin (using
`beancount.plugins.implicit_prices` is recommend to get prices for all costs in
the Beancount file).

- "At Cost" - Show all inventories at cost, e.g., a position of
  `10 STOCK {4 USD}` would be converted to `40 USD`.
- "At Market Value" - Show all inventories at their current market value, that
  is, convert to the cost currency at the current price. E.g., a position of
  `10 STOCK {4 USD}` would be converted to `50 USD` if the current price of
  `STOCK` is `5 USD`.
- "Units" - The plain units of all positions, e.g., `10 STOCK` for a position of
  `10 STOCK {4 USD}`.
- "Converted to X" - Convert to the currency `X`, e.g., a position of
  `10 STOCK {4 USD}` would be converted to `20 X` if the current price of
  `STOCK` is `2 X`. For positions with a price, a conversion via the cost
  currency is attempted if no direct price exists, so the example position would
  also successfully be converted if no price for `STOCK` in `X` exists but both
  a price of `STOCK` in `USD` and a price of `X` in `USD` exists.
- "Converted to X,Y" - It is also possible to chain conversions to currencies by
  selecting multiple conversions in the dropdown. These conversions are done in
  sequence, a position of `10 STOCK {4 USD}` would first be converted to `X` and
  then this amount in `X` would be converted to `Y`.

None of the conversions will silently drop amounts, so if a conversion is not
possible, the un-converted units are shown.
