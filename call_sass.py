#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Organizes the input arguments and sends job to sass."""

import argparse

from sass.sass_runner import SassCalibrationRunner
from sass import logger, utilities


def main():
    """Organizes the input arguments and sends job to sass."""
    parser = argparse.ArgumentParser(description='Run source collector')
    parser.add_argument('-t1', '--start', dest='start', required=True, type=str,
                        help='Start date, UTC timestamp (e.g., 2012-02-07T13:30:00Z)')
    parser.add_argument('-t2', '--end', dest='end', required=True, type=str,
                        help='End date, UTC timestamp (e.g., 2012-02-07T13:30:00Z)')
    parser.add_argument('-s', '--set', dest='set_id', required=False, type=str,
                        help='Id of the set of instruments to process')

    args = parser.parse_args()

    set_id = args.set_id
    start = utilities.parse_datetime(args.start)
    end = utilities.parse_datetime(args.end)

    if start > end:
        logger.error('Invalid dates given: Start date is after end date')
        exit(1)

    # then do something!
    runner = SassCalibrationRunner()
    runner.run(start=start, end=end, set_id=set_id)


if __name__ == '__main__':
    main()
