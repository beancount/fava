"""Adding a forecasting feature to Beancount via a plugin

see https://github.com/beancount/beancount/blob/ab3fdc613fd408e5f6d8039b2fe7eb37c0b31a5e/experiments/plugins/forecast.py
also https://github.com/beancount/beancount/blob/d841487ccdda04c159de86b1186e7c2ea997a3e2/beancount/parser/lexer.l#L127-L129

This entry filter plugin uses existing syntax to define and automatically
insert future transactions based on a convention.

A User can create a transaction like this:

    plugin "fava.plugins.forecast" "{'years':5}"

    2022-01-24 open Assets:Checking USD

    2021-02-01 # "Rent"
        frequency: "monthly" ; required
        interval: 1
        Assets:Checking         500 USD
        Income:Other

These transactions will be filtered out and replaced with new transactions
for the period specified in the configuration string (default: 5 years)

see https://dateutil.readthedocs.io/en/stable/rrule.html#dateutil.rrule.rrule for metadata

"""

import calendar
from dateutil.rrule import rrule, FREQNAMES
from datetime import date # pip install DateTime

from beancount.core import data
from beancount.core.amount import Amount #, mul
from beancount.core.number import D, ZERO, Decimal
# from beancount import loader

__plugins__ = ('forecast', ) 

multiplier = {
    'YEARLY': 1,
    'MONTHLY': 12,
    'WEEKLY': 56,
    'DAILY': 365.25,
}

def forecast(entries, options_map, config_str=None):
    """A filter that piggybacks on top of the Beancount input syntax to
    insert forecast entries automatically. This function accepts the return
    value of beancount.loader.load_file() and must return the same type of output.

    Args:
        entries: a list of entry instances
        options_map: a dict of options parsed from the file
        config_str: a dict of plugin-specific options

    Returns:
        A tuple of entries and errors

    """
    errors = []
    config = eval(config_str, {}, {}) if config_str else {}

    # Filter out forecast entries from the list of valid entries
    forecast_entries = []
    filtered_entries = []
    accounts = {} # accounts with statement closing dates

    for entry in entries:
        if (isinstance(entry, data.Open) and entry.meta.get('statement-close')):
            accounts[entry.account] = entry.meta.get('statement-close')

        outlist = (forecast_entries
                    if (isinstance(entry, data.Transaction) and entry.flag == '#')
                    else filtered_entries)
        outlist.append(entry)

    # Generate forecast entries until meta.until
    new_entries = []

    for entry in forecast_entries:
        # Parse the periodicity
        if not 'frequency' in entry.meta:
            new_entries.append(entry)
            continue
        else:
            frequency = entry.meta['frequency'].upper() # TODO: error handling, default to YEARLY?
            freq = FREQNAMES.index(frequency)
            interval = entry.meta.get('interval', 1)
            _count = multiplier.get(frequency) * config.get('years', 5) / interval
            count = entry.meta.get('count', _count)
            until = date.fromisoformat(entry.meta.get('until')) if entry.meta.get('until') else None

            # Generate a new entry for each forecast date
            # TODO: AFTER the last cleared entry
            try:
                forecast_dates = [dt.date() for dt in rrule(freq=freq, dtstart=entry.date, count=count, interval=interval, until=until)]

                for forecast_date in forecast_dates:
                    forecast_entry = entry._replace(date=forecast_date)

                    # add tags
                    for posting in entry.postings:
                        statement_close = accounts.get(posting.account)

                        if(statement_close):
                            month = forecast_date.month
                            link = ""

                            if (forecast_date.day > statement_close):
                                link = calendar.month_name[month + 1 if month < 12 else 1].lower() + "-" + str(forecast_date.year if month < 12 else forecast_date.year + 1)
                            else:
                                link = calendar.month_name[month].lower() + "-" + str(forecast_date.year)

                            new_links = set(entry.links)
                            new_links.add(link)
                            forecast_entry = forecast_entry._replace(links=new_links)

                    # forecast_entry = entry._replace(date=forecast_date, links=new_links)
                    new_entries.append(forecast_entry)

            except:
                print("Error in Transaction Metadata:")
                # print(entry)
                print(entry.meta)
                # print("=====\n")

    # print(forecast_dates)
    # print(new_entries)
    return filtered_entries + new_entries, errors
    # return filtered_entries + new_entries, []