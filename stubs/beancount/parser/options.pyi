# pylint: disable=missing-docstring,unused-argument,multiple-statements
from beancount.core.account_types import AccountTypes

from fava.util.typing import BeancountOptions

OPTIONS_DEFAULTS: BeancountOptions

def get_account_types(
    options: BeancountOptions,
) -> AccountTypes: ...
