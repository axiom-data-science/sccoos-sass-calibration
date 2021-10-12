#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Organizes the input arguments and sends job to sass."""

import argparse

from dateutil.relativedelta import relativedelta
from datetime import datetime

from sass.sass_runner import SassCalibrationRunner
from sass import logger, utilities


def main():
    """Organizes the input arguments and sends job to sass."""
    parser = argparse.ArgumentParser(description='Run SCCOOS Automated Shore Station (SASS) '
                                                 'calibration calculations for Chloroohyll, O2, '
                                                 'and pH.')
    parser.add_argument('-t1', '--start', dest='start', required=False, type=str,
                        help='Start date as yyyy-mm-dd. If omitted, '
                             'presumes the most recent 5 days.')
    parser.add_argument('-t2', '--end', dest='end', required=False, type=str,
                        help='End date as yyyy-mm-dd. If omitted, presumes a singe day '
                             'that is determined by START')
    parser.add_argument('-s', '--set', dest='set_id', required=True, type=str,
                        help='Id of the set of instruments to process. '
                             'Must be defined in instrument_sets.json')

    args = parser.parse_args()

    set_id = args.set_id
    if args.start and args.end:
        start = utilities.parse_datetime(args.start + "T00:00:00Z")
        end = utilities.parse_datetime(args.end + "T00:00:00Z")
    elif args.start and not args.end:  # just do one day
        start = utilities.parse_datetime(args.start + "T00:00:00Z")
        end = start
    else:  # do most recent 5 days
        end = datetime.utcnow()
        start = end - relativedelta(days=4)

    if start > end:
        logger.error('Invalid dates given: Start date is after end date')
        exit(1)

    # then do something!
    runner = SassCalibrationRunner()
    runner.run(start=start, end=end, set_id=set_id)


if __name__ == '__main__':
    main()
