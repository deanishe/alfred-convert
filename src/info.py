#!/usr/bin/python
# encoding: utf-8
#
# Copyright  (c) 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-12-26
#

"""info.py [options] [<query>]

View/manage workflow settings.

Usage:
    info.py [<query>]
    info.py (-h|--help)
    info.py --openhelp
    info.py --openactive
    info.py --openunits
    info.py --openapi
    info.py --currencies [<query>]

Options:
    -h, --help    Show this message
    --openhelp    Open help file in default browser
    --openactive  Open active currency file in default editor
    --openunits   Open custom units file in default editor
    --openapi     Open the openexchangerates.org signup page
    --currencies  View/search supported currencies

"""

from __future__ import absolute_import

from datetime import timedelta
import subprocess
import sys

from docopt import docopt

from workflow import (
    ICON_INFO,
    ICON_WARNING,
    ICON_WEB,
    MATCH_ALL,
    MATCH_ALLCHARS,
    Workflow3,
)
from workflow.util import run_trigger

from config import (
    bootstrap,
    ACTIVE_CURRENCIES_FILENAME,
    CURRENCIES,
    CRYPTO_CURRENCIES,
    CURRENCY_CACHE_NAME,
    CUSTOM_DEFINITIONS_FILENAME,
    ICON_CURRENCY,
    ICON_HELP,
    README_URL,
)

# Signup page for free API key
SIGNUP_URL = 'https://openexchangerates.org/signup/free'

log = None

DELIMITER = u'\u203a'  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK


def human_timedelta(td):
    """Return relative time (past) in human-readable format.

    Example: "10 minutes ago"

    Args:
        td (datetime.timedelta): Time delta to convert.

    Returns:
        unicode: Human-readable time delta.

    """
    output = []
    d = {'day': td.days}
    d['hour'], rem = divmod(td.seconds, 3600)
    d['minute'], d['second'] = divmod(rem, 60)

    for unit in ('day', 'hour', 'minute', 'second'):
        i = d[unit]

        if i == 1:
            output.append('1 %s' % unit)

        elif i > 1:
            output.append('%d %ss' % (i, unit))
        
        # we want to ignore only leading zero values
        # otherwise we'll end up with times like
        # "3 days and 10 seconds"
        elif len(output):
            output.append(None)

    if len(output) > 2:
        output = output[:2]

    # strip out "Nones" to leave only relevant units
    output = [s for s in output if s is not None]
    output.append('ago')
    return ' '.join(output)


def handle_delimited_query(query):
    """Process sub-commands.

    Args:
        query (str): User query

    """
    # Currencies or decimal places
    if query.endswith(DELIMITER):  # User deleted trailing space
        run_trigger('config')
        # subprocess.call(['osascript', '-e', ALFRED_AS])
        # return

    mode, query = [s.strip() for s in query.split(DELIMITER)]

    if mode == 'currencies':

        currencies = sorted([(name, symbol) for (symbol, name)
                            in CURRENCIES.items()] +
                            [(name, symbol) for (symbol, name)
                            in CRYPTO_CURRENCIES.items()])

        if query:
            currencies = wf.filter(query, currencies,
                                   key=lambda t: ' '.join(t),
                                   match_on=MATCH_ALL ^ MATCH_ALLCHARS,
                                   min_score=30)

        else:  # Show last update time
            age = wf.cached_data_age(CURRENCY_CACHE_NAME)
            if age > 0:  # Exchange rates in cache
                td = timedelta(seconds=age)
                wf.add_item('Exchange rates updated {}'.format(
                            human_timedelta(td)),
                            icon=ICON_INFO)

        if not currencies:
            wf.add_item('No matching currencies',
                        'Try a different query',
                        icon=ICON_WARNING)

        for name, symbol in currencies:
            wf.add_item(u'{} // {}'.format(name, symbol),
                        u'Use `{}` in conversions'.format(symbol),
                        copytext=symbol,
                        valid=False,
                        icon=ICON_CURRENCY)

        wf.send_feedback()


def main(wf):
    """Run Script Filter.

    Args:
        wf (workflow.Workflow): Workflow object.

    """
    args = docopt(__doc__, wf.args)

    log.debug('args : {!r}'.format(args))

    query = args.get('<query>')

    bootstrap(wf)

    # Alternative actions ----------------------------------------------

    if args.get('--openapi'):
        subprocess.call(['open', SIGNUP_URL])
        return

    if args.get('--openhelp'):
        subprocess.call(['open', README_URL])
        return

    if args.get('--openunits'):
        path = wf.datafile(CUSTOM_DEFINITIONS_FILENAME)
        subprocess.call(['open', path])
        return

    if args.get('--openactive'):
        path = wf.datafile(ACTIVE_CURRENCIES_FILENAME)
        subprocess.call(['open', path])
        return

    # Parse query ------------------------------------------------------

    if DELIMITER in query:
        return handle_delimited_query(query)

    # Filter options ---------------------------------------------------

    query = query.strip()

    options = [
        dict(title='View Help File',
             subtitle='Open help file in your browser',
             valid=True,
             arg='--openhelp',
             icon=ICON_HELP),

        dict(title='View All Supported Currencies',
             subtitle='View and search list of supported currencies',
             autocomplete=u'currencies {} '.format(DELIMITER),
             icon=ICON_CURRENCY),

        dict(title='Edit Active Currencies',
             subtitle='Edit the list of active currencies',
             valid=True,
             arg='--openactive',
             icon='icon.png'),

        dict(title='Edit Custom Units',
             subtitle='Add and edit your own custom units',
             valid=True,
             arg='--openunits',
             icon='icon.png'),

        dict(title='Get API key',
             subtitle='Sign up for free openexchangerates.org account',
             valid=True,
             arg='--openapi',
             icon=ICON_WEB),
    ]

    if query:
        options = wf.filter(query, options, key=lambda d: d['title'],
                            min_score=30)

    if not options:
        wf.add_item('No matching options', 'Try a different query?',
                    icon=ICON_WARNING)

    for d in options:
        wf.add_item(**d)

    wf.send_feedback()
    return


if __name__ == '__main__':
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
