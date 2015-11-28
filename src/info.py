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
    info.py --openunits
    info.py --currencies [<query>]
    info.py --places <query>

Options:
    -h, --help    Show this message
    --openhelp    Open help file in default browser
    --openunits   Open custom units file in default editor
    --currencies  View/search supported currencies
    --places      Set decimal places

"""

from __future__ import print_function, unicode_literals, absolute_import

from datetime import timedelta
import os
import shutil
import subprocess
import sys

from vendor.docopt import docopt

from workflow import (
    ICON_HELP,
    ICON_INFO,
    ICON_SETTINGS,
    ICON_WARNING,
    MATCH_ALL,
    MATCH_ALLCHARS,
    Workflow,
)

from config import (
    CURRENCIES,
    CURRENCY_CACHE_NAME,
    CUSTOM_DEFINITIONS_FILENAME,
    DECIMAL_PLACES_DEFAULT,
    ICON_CURRENCY,
    KEYWORD_SETTINGS,
    README_URL,
)

log = None

DELIMITER = '\u203a'  # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK

ALFRED_AS = 'tell application "Alfred 2" to search "{0}"'.format(
    KEYWORD_SETTINGS)


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

        if unit == 'second' and len(output):
            # no seconds unless last update was < 1m ago
            break

        if i == 1:
            output.append('1 %s' % unit)

        elif i > 1:
            output.append('%d %ss' % (i, unit))

    output.append('ago')
    return ' '.join(output)


def main(wf):
    """Run Script Filter.

    Args:
        wf (workflow.Workflow): Workflow object.

    Returns:
        int: Exit status.
    """
    args = docopt(__doc__, wf.args)

    log.debug('args : {!r}'.format(args))

    query = args.get('<query>')

    if args.get('--openhelp'):
        subprocess.call(['open', README_URL])
        return 0

    if args.get('--openunits'):
        path = wf.datafile(CUSTOM_DEFINITIONS_FILENAME)
        if not os.path.exists(path):
            shutil.copy(
                wf.workflowfile('{0}.sample'.format(
                                CUSTOM_DEFINITIONS_FILENAME)),
                path)

        subprocess.call(['open', path])
        return 0

    if args.get('--places'):
        value = int(query)
        log.debug('Setting `decimal_places` to {!r}'.format(value))
        wf.settings['decimal_places'] = value
        print('Set decimal places to {}'.format(value))
        # subprocess.call(['osascript', '-e', ALFRED_AS])
        return 0

    if not query or not query.strip():
        wf.add_item('View Help File',
                    'Open help file in your browser',
                    valid=True,
                    arg='--openhelp',
                    icon=ICON_HELP)

        wf.add_item('View Supported Currencies',
                    'View and search list of supported currencies',
                    autocomplete=' currencies {0} '.format(DELIMITER),
                    icon=ICON_CURRENCY)

        wf.add_item(('Decimal Places in Results '
                    '(current : {0})'.format(wf.settings.get(
                                            'decimal_places',
                                            DECIMAL_PLACES_DEFAULT))),
                    'View and search list of supported currencies',
                    autocomplete=' places {0} '.format(DELIMITER),
                    icon=ICON_SETTINGS)

        wf.add_item('Edit Custom Units',
                    'Add and edit your own custom units',
                    valid=True,
                    arg='--openunits',
                    icon='icon.png')

        wf.send_feedback()
        return 0

    else:  # Currencies or decimal places
        if query.endswith(DELIMITER):  # User deleted trailing space
            subprocess.call(['osascript', '-e', ALFRED_AS])
            return 0

        mode, query = [s.strip() for s in query.split(DELIMITER)]

        if mode == 'currencies':

            currencies = sorted([(name, symbol) for (symbol, name)
                                in CURRENCIES.items()])

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
                wf.add_item('{0} // {1}'.format(name, symbol),
                            'Use `{0}` in conversions'.format(symbol),
                            icon=ICON_CURRENCY)

            wf.send_feedback()

        elif mode == 'places':

            if query:
                if not query.isdigit():
                    wf.add_item('Invalid number : {0}'.format(query),
                                'Please enter a number',
                                icon=ICON_WARNING)
                else:
                    wf.add_item('Set decimal places to : {0}'.format(query),
                                'Hit `ENTER` to save',
                                valid=True,
                                arg='--places {0}'.format(query),
                                icon=ICON_SETTINGS)
            else:
                wf.add_item('Enter a number of decimal places',
                            'Current number is {0}'.format(
                                wf.settings.get('decimal_places',
                                                DECIMAL_PLACES_DEFAULT)),
                            icon=ICON_INFO)

            wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
