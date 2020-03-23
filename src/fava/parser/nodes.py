"""Handlers for all node types returned by the tree-sitter parser."""
# pylint: disable=unused-argument,redefined-builtin
import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Type
from typing import Union

from beancount.core.account import TYPE
from beancount.core.amount import Amount
from beancount.core.data import Balance
from beancount.core.data import Booking
from beancount.core.data import Close
from beancount.core.data import Commodity
from beancount.core.data import Custom
from beancount.core.data import Document
from beancount.core.data import EMPTY_SET
from beancount.core.data import Event
from beancount.core.data import Note
from beancount.core.data import Open
from beancount.core.data import Pad
from beancount.core.data import Posting
from beancount.core.data import Price
from beancount.core.data import Query
from beancount.core.data import Transaction
from beancount.core.number import Decimal
from beancount.core.number import MISSING
from beancount.core.number import ZERO
from beancount.core.position import CostSpec
from beancount.parser.grammar import ValueType
from tree_sitter import Node


class IncludeFound(Exception):
    """Signal an include directive."""

    __slots__ = ("filename",)

    def __init__(self, filename: str) -> None:
        super().__init__()
        self.filename = filename


def include(state, node: Node) -> None:
    """Handle a include directive node."""
    filename = state.handle_node(node.children[1])
    raise IncludeFound(filename)


def option(state, node: Node) -> None:
    """Handle an option directive."""
    state.handle_option(node, state.get(node, "key"), state.get(node, "value"))


def plugin(state, node: Node) -> None:
    """Handle a plugin directive node."""
    state.options["plugin"].append(
        (state.get(node, "name"), state.get(node, "config"))
    )


def pushtag(state, node: Node) -> None:
    """Handle a pushtag directive node."""
    tag_ = state.get(node, "tag")
    state.tags.add(tag_)


def poptag(state, node: Node) -> None:
    """Handle a pushtag directive node."""
    tag_ = state.get(node, "tag")
    try:
        state.tags.remove(tag_)
    except KeyError:
        state.error(node, "Attempting to pop absent tag: '{}'".format(tag_))


def pushmeta(state, node: Node) -> None:
    """Handle a pushmeta directive node."""
    key_, value = state.get(node, "key_value")
    state.meta[key_].append(value)


def popmeta(state, node: Node) -> None:
    """Handle a popmeta directive node."""
    key_: str = state.get(node, "key")
    try:
        if key_ not in state.meta:
            raise IndexError
        value_list = state.meta[key_]
        value_list.pop(-1)
        if not value_list:
            state.meta.pop(key_)
    except IndexError:
        state.error(
            node, "Attempting to pop absent metadata key: '{}'".format(key_)
        )


def document(state, node: Node) -> Document:
    """Handle a document directive."""
    tags, links = state.get(node, "tags_and_links") or (set(), EMPTY_SET)
    if state.tags:
        tags.update(state.tags)
    return Document(
        state.metadata(node),
        state.get(node, "date"),
        state.get(node, "account"),
        state.get(node, "filename"),
        frozenset(tags) if tags else EMPTY_SET,
        frozenset(links) if links else EMPTY_SET,
    )


def commodity(state, node: Node) -> Commodity:
    """Handle a commodity entry."""
    return Commodity(
        state.metadata(node),
        state.get(node, "date"),
        state.get(node, "currency"),
    )


def event(state, node: Node) -> Event:
    """Handle an event entry."""
    return Event(
        state.metadata(node),
        state.get(node, "date"),
        state.get(node, "type"),
        state.get(node, "description"),
    )


def close(state, node: Node) -> Close:
    """Handle a close entry."""
    return Close(
        state.metadata(node),
        state.get(node, "date"),
        state.get(node, "account"),
    )


def balance(state, node: Node) -> Balance:
    """Handle a balance entry."""
    amount_with_tolerance = state.get(node, "amount")
    amo: Amount
    if isinstance(amount_with_tolerance, Amount):
        amo = amount_with_tolerance
        tolerance = None
    else:
        amo, tolerance = amount_with_tolerance
    return Balance(
        state.metadata(node),
        state.get(node, "date"),
        state.get(node, "account"),
        amo,  # type: ignore
        tolerance,
        None,
    )


def open(state, node: Node) -> Open:
    """Handle an open entry."""
    booking = state.get(node, "booking")
    if booking is not None:
        booking = getattr(Booking, booking)
        state.error(node, "Invalid booking method: {}".format(booking))
        if booking is None:
            booking = state.options["booking_method"]
    return Open(
        state.metadata(node),
        state.get(node, "date"),
        state.get(node, "account"),
        state.get(node, "currencies"),
        booking,
    )


def pad(state, node: Node) -> Pad:
    """Handle a pad entry."""
    return Pad(
        state.metadata(node),
        state.get(node, "date"),
        state.get(node, "account"),
        state.get(node, "from_account"),
    )


def custom(state, node: Node) -> Custom:
    """Handle a custom entry."""
    custom_values = []
    for child in node.children[3:]:
        val = state.handle_node(child)
        dtype = TYPE if child.type == "account" else type(val)
        custom_values.append(ValueType(val, dtype))
    return Custom(
        state.metadata(node),
        state.get(node, "date"),
        state.get(node, "name"),
        custom_values,
    )


def note(state, node: Node) -> Note:
    """Handle a Note entry.

    A note attaches some comment to an account on a given day."""
    return Note(
        state.metadata(node),
        state.get(node, "date"),
        state.get(node, "account"),
        state.get(node, "note"),
    )


def price(state, node: Node) -> Price:
    """Handle a price entry."""
    return Price(
        state.metadata(node),
        state.get(node, "date"),
        state.get(node, "currency"),
        state.get(node, "amount"),
    )


def query(state, node: Node) -> Query:
    """Handle a query entry."""
    return Query(
        state.metadata(node),
        state.get(node, "date"),
        state.get(node, "name"),
        state.get(node, "query"),
    )


def transaction(state, node: Node) -> Transaction:
    """Handle a Transaction entry."""
    tags, links = state.get(node, "tags_and_links") or (set(), EMPTY_SET)
    if state.tags:
        tags.update(state.tags)
    strings: Tuple[Optional[str], str] = (
        state.get(node, "txn_strings") or (None, "")
    )

    return Transaction(
        state.metadata(node),
        state.get(node, "date"),
        state.get(node, "flag"),
        *strings,
        frozenset(tags) if tags else EMPTY_SET,
        frozenset(links) if links else EMPTY_SET,
        state.get(node, "postings"),
    )


def txn_strings(state, node: Node):
    """Handle transaction strings:
    payee and narration or just narration."""
    children = tuple(map(state.handle_node, node.children))
    if len(children) == 1:
        return None, children[0]
    return children


def postings(state, node: Node) -> List[Posting]:
    """Handle a list of postings."""
    return list(map(state.handle_node, node.children))


def price_annotation(state, node: Node):
    """Handle a price annotation."""
    if len(node.children) > 1:
        istotal = node.children[0].type == "@@"
        return state.handle_node(node.children[1]), istotal
    return MISSING


def cost_spec(state, node: Node) -> CostSpec:
    """Handle a cost spec."""
    # pylint: disable=too-many-branches
    istotal = node.children[0].type != "{"
    cost_comp_list_ = state.handle_node(node.children[1])
    if not cost_comp_list_:
        return CostSpec(MISSING, None, MISSING, None, None, False)

    compound_cost = None
    date_ = None
    label = None
    merge = None

    for comp in cost_comp_list_:
        if comp.type == "compound_amount":
            if compound_cost is None:
                compound_cost = state.handle_node(comp)
            else:
                state.error(comp, "Duplicate cost.")
        elif comp.type == "date":
            if date_ is None:
                date_ = state.handle_node(comp)
            else:
                state.error(comp, "Duplicate date.")
        elif comp.type == "*":
            if merge is None:
                merge = True
                state.error(comp, "Cost merging is not supported yet.")
            else:
                state.error(comp, "Duplicate merge-cost spec.")
        else:
            if label is None:
                label = state.handle_node(comp)
            else:
                state.error(comp, "Duplicate label.")

    number_per: Union[Decimal, Type[MISSING]]
    if compound_cost is None:
        number_per, number_total, currency_ = MISSING, None, MISSING
    else:
        number_per, number_total, currency_ = compound_cost
        if istotal:
            if number_total is not None:
                state.error(
                    node,
                    "Per-unit cost may not be specified using "
                    "total cost syntax. Ignoring per-unit cost.",
                )
                number_per = ZERO
            else:
                number_total = number_per
                number_per = ZERO

    merge = merge or False
    return CostSpec(number_per, number_total, currency_, date_, label, merge)


def cost_comp_list(state, node: Node):
    """Handle a list of cost spec component."""
    return list(map(state.handle_node, node.children))


def cost_comp(state, node: Node):
    """Handle a cost spec component."""
    return node.children[0]


def compound_amount(state, node: Node) -> Tuple[Decimal, Decimal, str]:
    """Handle a compound amount."""
    number_per = state.get(node, "number_per")
    number_total = state.get(node, "number_total")
    currency_ = state.get(node, "currency")
    if currency_ is not None:
        state.dcupdate(number_per, currency_)
        state.dcupdate(number_total, currency_)
    return (
        number_per,
        number_total,
        currency_,
    )


def posting(state, node: Node) -> Posting:
    """Handle a single posting."""
    units = state.get(node, "amount")
    price_ = state.get(node, "price_annotation")
    if price_ is not None and price_ is not MISSING:
        price_, istotal = price_
        if (
            price_
            and isinstance(price_.number, Decimal)
            and price_.number < ZERO
        ):
            state.error(node.children[0], "Negative prices are not allowed")
        if istotal:
            if units.number == ZERO:
                num = ZERO
            else:
                num = price_.number / abs(units.number)
            price_ = Amount(num, price_.currency)
    return Posting(
        state.get(node, "account"),
        units,
        state.get(node, "cost_spec"),
        price_,
        state.get(node, "flag"),
        state.metadata(node.children[0]),
    )


def metadata(state, node: Node) -> Dict[str, Any]:
    """Handle metadata."""
    meta = {}
    for child in node.children:
        key_value_ = state.handle_node(child)
        meta[key_value_[0]] = key_value_[1]
    return meta


def currency_list(state, node: Node) -> List[str]:
    """Handle a currency list."""
    currencies = []
    for child in node.children:
        if child.type == "currency":
            currencies.append(state.handle_node(child))
    return currencies


def key_value(state, node: Node) -> Tuple[str, Optional[Any]]:
    """Handle a key/value line."""
    try:
        return (
            state.handle_node(node.children[0]),
            state.handle_node(node.children[1]),
        )
    except IndexError:
        return (state.handle_node(node.children[0]), None)


def tags_and_links(state, node: Node) -> Tuple[Set, Set]:
    """Tags and links."""
    tags, links = set(), set()
    for child in node.children:
        typ = child.type
        if typ == "link":
            links.add(state.handle_node(child))
        elif typ == "tag":
            tags.add(state.handle_node(child))
    return tags, links


def unary_num_expr(state, node: Node) -> Decimal:
    """Handle a unary numerical expression."""
    operator = node.children[0].type
    num = state.handle_node(node.children[1])
    if operator == "-":
        return -num
    return num


def binary_num_expr(state, node: Node) -> Decimal:
    """Handle a binary numerical expression."""
    operator = node.children[1].type
    left = state.handle_node(node.children[0])
    right = state.handle_node(node.children[2])
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    assert operator == "/"
    return left / right


def incomplete_amount(state, node: Node):
    """An amount, where one of number and currency might be missing."""
    num, cur = MISSING, MISSING
    for child in node.children:
        typ = child.type
        if typ == "currency":
            cur = state.handle_node(child)
        else:
            num = state.handle_node(child)
    state.dcupdate(num, cur)
    return Amount(num, cur)  # type: ignore


amount = incomplete_amount  # pylint: disable=invalid-name


def date(state, node: Node) -> datetime.date:
    """Handle a date token."""
    contents = state.contents
    year = contents[node.start_byte : node.start_byte + 4]
    month = contents[node.start_byte + 5 : node.start_byte + 7]
    day = contents[node.start_byte + 8 : node.start_byte + 11]
    return datetime.date(int(year), int(month), int(day))


def key(state, node: Node) -> str:
    """Handle a key token."""
    return state.contents[node.start_byte : node.end_byte - 1].decode()


def link(state, node: Node) -> str:
    """Handle a link token."""
    return state.contents[node.start_byte + 1 : node.end_byte].decode()


def tag(state, node: Node) -> str:
    """Handle a tag token."""
    return state.contents[node.start_byte + 1 : node.end_byte].decode()


def number(state, node: Node) -> Decimal:
    """Handle a number token."""
    return Decimal(state.contents[node.start_byte : node.end_byte].decode())


def string(state, node: Node) -> str:
    """Handle a string token."""
    return state.contents[node.start_byte + 1 : node.end_byte - 1].decode()


def currency(state, node: Node) -> str:
    """Handle a currency token."""
    name = state.contents[node.start_byte : node.end_byte].decode()
    state.options["commodities"].add(name)
    return name


def flag(state, node: Node) -> str:
    """Handle a flag token."""
    return state.contents[node.start_byte : node.end_byte].decode()


def account(state, node: Node) -> str:
    """Handle an account token."""
    return state.contents[node.start_byte : node.end_byte].decode()


def bool(state, node: Node):
    """Handle a boolean token."""
    return state.contents[node.start_byte : node.start_byte + 1] == b"T"
