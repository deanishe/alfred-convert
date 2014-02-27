#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-25
#

"""
Runs as daemon process in the background and updates exchange rates.
"""

from __future__ import print_function, unicode_literals

import os
import sys

from config import CURRENCY_CACHE_NAME, CURRENCY_CACHE_AGE, UPDATE_STATUS_FILE
from currency import fetch_currency_rates
from workflow import Workflow


def daemonise(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    """This forks the current process into a daemon.
    The stdin, stdout, and stderr arguments are file names that
    will be opened and be used to replace the standard file descriptors
    in sys.stdin, sys.stdout, and sys.stderr.
    These arguments are optional and default to /dev/null.
    Note that stderr is opened unbuffered, so
    if it shares a file with stdout then interleaved output
    may not appear in the order that you expect.

    """

    # Do first fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)  # Exit first parent.
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    # Decouple from parent environment.
    os.chdir("/")
    os.umask(0)
    os.setsid()
    # Do second fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)  # Exit second parent.
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    # Now I am a daemon!
    # Redirect standard file descriptors.
    si = file(stdin, 'r', 0)
    so = file(stdout, 'a+', 0)
    se = file(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())


def process_exists(pid):
    """Does a process with PID ``pid`` actually exist?

    :returns: `True` or `False`

    """

    try:
        os.kill(pid, 0)
    except OSError:  # not running
        return False
    return True


def main(wf):
    daemonise()
    statuspath = wf.cachefile(UPDATE_STATUS_FILE)

    # Check for running instance
    if os.path.exists(statuspath):
        pid = int(open(statuspath, 'rb').read())
        if process_exists(pid):
            wf.logger.debug('instance already running')
            sys.exit(0)

    # Save PID to file and update exchange rates
    open(statuspath, 'wb').write('%s' % os.getpid())
    # Insert delay to check info message is posted in Alfred
    # import time
    # time.sleep(10)
    wf.logger.debug('Fetching exchange rates from ECB ...')
    try:
        exchange_rates = wf.cached_data(CURRENCY_CACHE_NAME,
                                        fetch_currency_rates,
                                        CURRENCY_CACHE_AGE)
    finally:
        if os.path.exists(statuspath):
            os.unlink(statuspath)
    wf.logger.debug('Exchange rates updated.')
    for currency, rate in exchange_rates.items():
        wf.logger.debug('1 EUR = {0} {1}'.format(rate, currency))


if __name__ == '__main__':
    wf = Workflow()
    wf.run(main)
