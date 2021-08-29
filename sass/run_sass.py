#!python
# coding=utf-8
import argparse
from dateutil import parser as dateparser
from datetime import datetime, timezone
import json
from pathlib import Path


here = Path(__file__).parent
stations_filename = 'config/stations.json'
instrumentset_filename = 'config/instrument_sets.json'


def read_config(filename):
    """ read the file that contains the urls and columns names for different installations

    :returns: a dictionary of instrument set configuration
    """
    path = here.joinpath(filename)
    with open(str(path), "r") as f:
        config = json.loads(f.read())
    return config


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

    print(f"{start} to {end} for station {station_id}")



    # then do something!
    instrument_sets = read_config(instrumentset_filename)
    print(instrument_sets)

    # sass(start, end, station_id)


if __name__ == '__main__':
    main()
