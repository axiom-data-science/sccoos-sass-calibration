#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Organizes the input arguments and sends job to sass."""

import argparse
from pathlib import Path

from dateutil.relativedelta import relativedelta
from datetime import datetime

from sass.sass_runner import SassCalibrationRunner, load_configs
from sass import logger, utilities

here = Path(__file__).parent
instrument_set_filename = 'sass/config/instrument_sets.json'


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
                             'Must be defined in instrument_sets.json or be "all" to do all active instrument sets.')

    args = parser.parse_args()

    set_id = args.set_id
    if args.start and args.end:
        start = utilities.parse_datetime(args.start + "T00:00:00Z")
        end = utilities.parse_datetime(args.end + "T00:00:00Z")
    elif args.start and not args.end:  # just do one day
        start = utilities.parse_datetime(args.start + "T00:00:00Z")
        end = start
    else:  # do most recent 5 days
        end = datetime.now()
        end = end.replace(hour=0, minute=0, second=0, microsecond=0)
        end = utilities.parse_datetime(end)
        start = end - relativedelta(days=4)

    if start > end:
        logger.error('Invalid dates given: Start date is after end date')
        exit(1)

    print(start)
    # then do something!
    runner = SassCalibrationRunner()
    if set_id != 'all':
        runner.run(start=start, end=end, set_id=set_id)
    else:
        path = here.joinpath(instrument_set_filename)
        instrument_sets = load_configs(path)
        for s in instrument_sets:
            runner.run(start=start, end=end, set_id=s.set_id)


if __name__ == '__main__':
    main()
