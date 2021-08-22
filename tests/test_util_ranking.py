# pylint: disable=missing-docstring
from datetime import date

from fava.util.ranking import ExponentialDecayRanker


def test_ranker():
    list_ = [1, 2, 3]
    ranker = ExponentialDecayRanker(list_)
    ranker.update(1, date(2015, 1, 1))
    ranker.update(2, date(2014, 1, 1))
    ranker.update(3, date(2016, 1, 1))
    assert ranker.sort() == [3, 1, 2]

    list_ = [1, 2]
    ranker = ExponentialDecayRanker(list_)
    ranker.update(2, date(2016, 1, 1))
    ranker.update(2, date(2016, 1, 1))
    ranker.update(1, date(2016, 1, 1))
    ranker.update(1, date(2016, 1, 2))
    assert ranker.sort() == [1, 2]

    list_ = [1, 2]
    ranker = ExponentialDecayRanker(list_)
    ranker.update(2, date(2015, 1, 1))
    ranker.update(2, date(2015, 1, 1))
    ranker.update(1, date(2016, 1, 1))
    assert ranker.sort() == [1, 2]

    list_ = [1, 2]
    ranker = ExponentialDecayRanker(list_)
    ranker.update(2, date(2015, 1, 1))
    ranker.update(2, date(2015, 1, 2))
    ranker.update(1, date(2016, 1, 1))
    assert ranker.sort() == [2, 1]
