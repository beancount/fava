"""Ranking utilities."""
import datetime
import math
from typing import Dict
from typing import List
from typing import Optional

ZERO = float()


class ExponentialDecayRanker:
    """Rank a list by exponential decay.

    Maintains scores for the items in a list. We can think of this as the sum
    of all 'likes', where the value of a 'like' starts at 1 and decays
    exponentially. So the current score would be given by (where `t` is the
    current time and `l` is the time of the 'like')

        s = Σ exp(-RATE * (t - l))

    As only the relative order on the items is relevant, we can multiply all
    scores by exp(RATE * t) and so we need to compute the following
    score:

        s = Σ exp(RATE * l)

    To avoid huge numbers, we actually compute and store the logarithm of that
    sum.

    Args:
        list_: If given, this list is ranked is by ``.sort()`` otherwise all
            items with at least one 'like' will be ranked.
        rate: This sets the rate of decay. ``1/rate`` will be the time (in
            days) that it takes for the value of a 'like' to decrease by
            ``1/e``. The default rate is set to ``math.log(2) * 1/365`` so
            that a 'like' from a year ago will count half as much as one from
            today.
    """

    __slots__ = ["list", "rate", "scores"]

    def __init__(
        self,
        list_: Optional[List[str]] = None,
        rate: float = math.log(2) * 1 / 365,
    ):
        self.list = list_
        self.rate = rate
        # We don't need to start with float('-inf') here as only the relative
        # scores matter.
        self.scores: Dict[str, float] = {}

    def update(self, item: str, date: datetime.date) -> None:
        """Add 'like' for item.

        Args:
            item: An item in the list that is being ranked.
            date: The date on which the item has been liked.
        """
        score = self.get(item)
        time = date.toordinal()
        higher = max(score, time * self.rate)
        lower = min(score, time * self.rate)
        self.scores[item] = higher + math.log1p(math.exp(lower - higher))

    def get(self, item: str) -> float:
        """Get the current score for an item, or zero."""
        return self.scores.get(item, ZERO)

    def sort(self) -> List[str]:
        """Return items sorted by rank."""
        if self.list is None:
            return sorted(self.scores.keys(), key=self.get, reverse=True)
        return sorted(self.list, key=self.get, reverse=True)
