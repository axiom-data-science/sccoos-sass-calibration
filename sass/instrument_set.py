#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Descriptions of instrument sets."""

from io import StringIO

import pandas as pd
from requests.exceptions import HTTPError
from dateutil.relativedelta import relativedelta

from . import utilities


class InstrumentSet:
    """Collects the information associated with a set of instrumentation installed at a site."""
    def __init__(self, set_id=None, start_date=None, end_date=None,
                 station_id=None, raw_data_url='', columns=[], calibration_locations={}, **kwargs):
        """Fills an InstrumentSet with information read from a JSON config file.

        :param set_id: unique identifier of the set (string)
        :param start_date: when the instrumentation was installed (ISO string)
        :param end_date: when the instrumentation was removed (ISO string)
        :param station_id:  where the InstrumentSet was installed (string)
        :param raw_data_url: where data for the InstrumentSet is posted publicly (string)
        :param columns: the column header for the raw data (list of strings)
        :param calibration_locations: dictionary of Google Sheet url and tab name/uid
        :param kwargs:
        """
        self.set_id = set_id
        self.start_date = start_date
        self.end_date = end_date
        self.station_id = station_id
        self.raw_data_url = raw_data_url
        self.columns = columns
        self.calibration_locations = calibration_locations
        if 'tab_names' in calibration_locations.keys():
            self.parameters = list(calibration_locations['tab_names'].keys())
        else:
            self.parameters = []

    def __repr__(self):
        """Returns a printable string."""
        return str(self)

    def __str__(self):
        """Returns a summary of the InstrumentSet."""
        return f'InstrumentSet{{id={self.set_id},parameters={self.parameters}}}'

    def build_urls(self, start, end):
        """Build a list of urls where can access the raw data.

        The urls are a list of daily files, in directories by month.

        :param start: datetime of earliest date
        :param end: datetime of latest date
        :return: list of strings that a URLs to daily data files
        """
        urls = []
        date = start
        while date < end:
            file_tag = date.strftime('%Y%m%d')
            dir_tag = date.strftime('%Y-%m')
            urls.append(f"{self.raw_data_url}{dir_tag}/data-{file_tag}.dat")
            date += relativedelta(days=1)

        return urls

    def retrieve_and_parse_raw_data(self, url, start, end) -> pd.DataFrame:
        """Read raw SASS data from URL and convert it to a DataFrame with headers.

        :param url: string url to the daily data file
        :param start: earliest datetime allowed
        :param end: latest datetime allowed
        :return: DataFrame of raw data
        """
        try:
            raw_dataset = utilities.requests_get(url)
        except HTTPError:
            # logger.warn(f"No data found for {station.foreignId} at {url}")
            return []

        # No column headers at all here
        names = self.columns
        data = pd.read_csv(StringIO(raw_dataset), names=names)

        # There are some corrupted lines that have only a subset of fields.
        # Who knows which fields remain so drop the whole line.
        # Corrupted lines all seem to be missing # - like that is where they were chopped.
        data.dropna(axis=0, subset=['temperature'], inplace=True)  # remove empty so can check ...
        data = data.loc[data['temperature'].str.contains('#'), :]  # that line has a hash mark

        # Files have a hash mark (#) to indicate the beginning of the data after date and IP.
        start_column = names[2]
        # So far, this is always temperature. If it isn't, I want to know so I can solve
        assert start_column == 'temperature'
        # Strip out that character and convert remaining to a number
        data[start_column] = data[start_column].str.replace('#', '')
        data[start_column] = data[start_column].str.strip().astype(float)

        # ensure that the "time" column has datetime values in UTC
        data["time"] = pd.to_datetime(data["sensor_time"], utc=True)
        data = data[(data['time'] >= start) & (data['time'] <= end)]

        return data
