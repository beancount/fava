"""Price helpers."""
from __future__ import annotations

import datetime
from bisect import bisect
from collections import Counter
from collections import defaultdict
from decimal import Decimal
from itertools import groupby
from typing import Callable
from typing import Iterable
from typing import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from typing import TypeAlias

    from fava.beans.abc import Price

    BaseQuote: TypeAlias = tuple[str, str]
    PricePoint: TypeAlias = tuple[datetime.date, Decimal]

ZERO = Decimal()
ONE = Decimal("1")


class DateKeyWrapper(Sequence[datetime.date]):
    """A class wrapping a list of prices for bisect.

    This is needed before Python 3.10, which adds the key argument.
    """

    __slots__ = ("inner",)

    def __init__(self, inner: list[PricePoint]) -> None:
        self.inner = inner

    def __len__(self) -> int:
        return len(self.inner)

    def __getitem__(self, k: int) -> datetime.date:  # type: ignore[override]
        return self.inner[k][0]


def _keep_last_per_day(
    prices: list[PricePoint],
) -> Iterable[PricePoint]:
    """In a sorted non-empty list of prices, keep the last one for each day."""
    last: PricePoint | None = None
    for price in prices:
        if last is not None and price[0] > last[0]:
            yield last
        last = price
    if last is not None:
        yield last


class FavaPriceMap:
    """A Fava alternative to Beancount's PriceMap.

    By having some more methods on this class, fewer helper functions need to
    be imported. Also, this is fully typed and allows to more easily reproduce
    issues with the whole price logic.

    This behaves slightly differently than Beancount. Beancount creates a list
    for each currency pair and then merges the inverse rates. We just create
    both the lists in tandem and count the directions that prices occur in.

    Args:
        price_entries: A sorted list of price entries.
    """

    def __init__(self, price_entries: list[Price]) -> None:
        raw_map: dict[BaseQuote, list[PricePoint]] = defaultdict(list)
        counts: Counter[BaseQuote] = Counter()

        for price in price_entries:
            rate = price.amount.number
            base_quote = (price.currency, price.amount.currency)
            raw_map[base_quote].append((price.date, rate))
            counts[base_quote] += 1
            if rate != ZERO:
                raw_map[(price.amount.currency, price.currency)].append(
                    (price.date, ONE / rate),
                )
        self._forward_pairs = [
            (base, quote)
            for (base, quote), count in counts.items()
            if counts.get((quote, base), 0) < count
        ]
        self._map = {
            k: list(_keep_last_per_day(rates)) for k, rates in raw_map.items()
        }

    def commodity_pairs(
        self,
        operating_currencies: list[str],
    ) -> list[BaseQuote]:
        """List pairs of commodities.

        Args:
            operating_currencies: A list of operating currencies.

        Returns:
            A list of pairs of commodities. Pairs of operating currencies will
            be given in both directions not just in the one most commonly found
            in the file.
        """
        forward_pairs = self._forward_pairs
        extra_operating_pairs = []
        for base, quote in forward_pairs:
            if base in operating_currencies and quote in operating_currencies:
                extra_operating_pairs.append((quote, base))
        return sorted(forward_pairs + extra_operating_pairs)

    def get_all_prices(self, base_quote: BaseQuote) -> list[PricePoint] | None:
        """Get all prices for the given currency pair."""
        return self._map.get(base_quote)

    def get_price(
        self,
        base_quote: BaseQuote,
        date: datetime.date | None = None,
    ) -> Decimal | None:
        """Get the price for the given currency pair."""
        return self.get_price_point(base_quote, date)[1]

    def get_price_point(
        self,
        base_quote: BaseQuote,
        date: datetime.date | None = None,
    ) -> PricePoint | tuple[None, Decimal] | tuple[None, None]:
        """Get the price point for the given currency pair."""
        base, quote = base_quote
        if base == quote:
            return (None, ONE)

        price_list = self._map.get(base_quote)
        if price_list is None:
            return (None, None)

        if date is None:
            return price_list[-1]

        index = bisect(DateKeyWrapper(price_list), date)
        if index == 0:
            return (None, None)
        return price_list[index - 1]

    def get_nested_price(
        self,
        base_quote: BaseQuote,
        date: datetime.date | None = None,
    ) -> Decimal | None:
        prices_number = self.get_price(base_quote, date)
        if prices_number is not None:
            # fast path
            return prices_number
        all_commodity = [
            commodity_pairs[0] for commodity_pairs in list(self._map.keys())
        ]
        groups = groupby(self._map.keys(), key=lambda x: x[0])
        conversions: dict[str, set[str]] = {}

        for key, group in groups:
            if key not in conversions:
                conversions[key] = set()
            conversions[key].update(
                commodity_pair[1] for commodity_pair in group
            )

        bellman_ford = BellmanFord(
            all_commodity,
            conversions,
            lambda x: self.get_price(x, date),
            start=base_quote[1],
        )
        r = bellman_ford.search()

        if base_quote[0] not in r:
            return None
        if r[base_quote[0]][1] is None:
            if base_quote[0] == base_quote[1]:
                return Decimal("1.00")
            return None
        return Decimal(1) / r[base_quote[0]][0]


class BellmanFord:
    """An Bellman-Ford algorithm implementation.

    optimized and modified for currency conversion scenarios.
    """

    def __init__(
        self,
        all_nodes: list[str],
        edges: dict[str, set[str]],
        get_widget: Callable[[BaseQuote], Decimal | None],
        start: str,
    ) -> None:
        self.searched = False
        self.get_widget = get_widget
        self.start = start
        self.all_nodes = all_nodes
        self.edges = edges

        table: dict[str, tuple[Decimal, str | None]] = {}
        # init table
        for n in all_nodes:
            table[n] = (Decimal("Infinity"), None)
        self.table = table

    def _get_path(self, end_node: str) -> Iterable[str]:
        if self.searched is False:
            self.search()
        r = [end_node]
        from_record = self.table.get(end_node)
        if from_record is None:
            return r
        while (
            from_record is not None
            and from_record[1] is not None
            and from_record[1] is not self.start
        ):
            if from_record[1] in r:
                return reversed(r)
            r.append(from_record[1])
            from_record = self.table.get(from_record[1])
        return reversed(r)

    def update_table(self) -> bool:
        updated = False
        for from_node in self.all_nodes:
            if self.table[from_node][0] == Decimal("Infinity"):
                continue
            edges = self.edges[from_node]
            for to in edges:
                widget = self.get_widget((from_node, to))
                if widget is None:
                    continue
                target_value = self.table[from_node][0] * widget
                if to == self.start:
                    continue
                if target_value.compare(self.table[to][0]) < 0 and (
                    self.table[to][0] - target_value
                ) > Decimal("0.00001"):
                    existed_path = list(self._get_path(to))
                    if from_node in existed_path:
                        continue
                    self.table[to] = (target_value, from_node)

                    updated = True

        return updated

    def print_table(self) -> None:
        heads = sorted(self.table.keys())
        print(  # noqa: T201
            "\n".join([str([t, self.table[t]]) for t in heads]),
        )
        print("+++++++++++++++++++++++++")  # noqa: T201

    def search(self) -> dict[str, tuple[Decimal, str | None]]:
        if self.searched is True:
            return self.table
        self.searched = True
        self.table[self.start] = (Decimal("1"), None)
        updated = True
        while updated:
            updated = self.update_table()
        return self.table
