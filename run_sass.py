#!python
# coding=utf-8
import argparse
from dateutil import parser as dateparser
from datetime import datetime, timezone
from sass import SassCalibrationRunner


def main():
    parser = argparse.ArgumentParser(description='Run source collector')
    parser.add_argument('-t1', '--start', dest='start', required=True, type=str,
                        help='Start date, UTC timestamp (e.g., 2012-02-07T13:30:00Z)')
    parser.add_argument('-t2', '--end', dest='end', required=True, type=str,
                        help='End date, UTC timestamp (e.g., 2012-02-07T13:30:00Z)')
    parser.add_argument('-s', '--station', dest='station_id', required=False, type=str,
                        help='Station name for doing just one (Optional)')

    args = parser.parse_args()

    station_id = args.station_id
    start = dateparser.parse(args.start)
    if args.end == 'now':
        end = datetime.now(timezone.utc)
    else:
        end = dateparser.parse(args.end)

    if start > end:
        # logger.error('Invalid dates given: Start date is after end date')
        print('Invalid dates given: Start date is after end date')
        exit(1)

    # then do something!
    SassCalibrationRunner.run(start=start, end=end, station_id=station_id)


if __name__ == '__main__':
    main()
