#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Descriptions of instrument sets."""

from io import StringIO
import datetime
import pathlib

import pandas as pd
from requests.exceptions import HTTPError
from dateutil.relativedelta import relativedelta

from sass import logger
from . import utilities


class InstrumentSet:
    """Collects the information associated with a set of instrumentation installed at a site."""
    def __init__(self, set_id=None, start_date=None, end_date=None,
                 station_id=None, raw_data_url='', columns=[], calibration_url='',
                 chlor_tab=None, chlor_gid=None,
                 o2_tab=None, o2_gid=None,
                 ph_tab=None, ph_gid=None, ph_salinity_set=None, **kwargs):
        """Fills an InstrumentSet with information read from a JSON config file.

        :param set_id: unique identifier of the set (string)
        :param start_date: when the instrumentation was installed (ISO string)
        :param end_date: when the instrumentation was removed (ISO string)
        :param station_id:  where the InstrumentSet was installed (string)
        :param raw_data_url: where data for the InstrumentSet is posted publicly (string)
        :param columns: the column header for the raw data (list of strings)
        :param calibration_url: dictionary of Google Sheet url and tab name/uid
        :param chlor_tab: Google sheet tab name for the Fluorometer (string)
        :param chlor_gid: Google sheet id code for the Fluorometer (string)
        :param o2_tab: Google sheet tab name for the Oxygen Sensor (string)
        :param o2_gid: Google sheet id code for the Oxygen Sensor (string)
        :param ph_tab: Google sheet tab name for the SeaFET (string)
        :param ph_gid: Google sheet id code for the SeaFET (string)
        :param ph_salinity_set: set_id of the instrument set that will provide salinity
        :param kwargs:
        """
        self.set_id = set_id
        self.start_date = start_date
        self.end_date = end_date
        self.station_id = station_id
        self.raw_data_url = raw_data_url
        self.data_columns = columns
        self.calibration_url = calibration_url
        self.cal_tabs = {
            'chlor': chlor_tab,
            'o2': o2_tab,
            'ph': ph_tab
        }
        self.cal_gids = {
            'chlor': chlor_gid,
            'o2': o2_gid,
            'ph': ph_gid
        }
        self.ph_salinity_set = ph_salinity_set
        self.parameters = []
        for key, value in self.cal_gids.items():
            if value:
                self.parameters.append(key)

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

        :param url: string url to the daily data file. can also be local file.
        :param start: earliest datetime allowed
        :param end: latest datetime allowed
        :return: DataFrame of raw data
        """
        names = self.data_columns
        if type(url) is pathlib.PosixPath:
            try:
                data = pd.read_csv(url, names=names, na_values=[-9.999, -0.999],
                                   encoding="ISO-8859-1")
            except FileNotFoundError:
                return pd.DataFrame({})
        else:
            try:
                raw_dataset = utilities.requests_get(url)
            except HTTPError:
                # logger.warn(f"No data found for {station.foreignId} at {url}")
                return pd.DataFrame({})

            # No column headers at all here
            data = pd.read_csv(StringIO(raw_dataset), names=names, na_values=[-9.999, -0.999])

        start_column = names[2]
        if start_column == 'temperature':  # I think CTD files always start with temperature
            # There are some corrupted lines that have only a subset of fields.
            # Who knows which fields remain so drop the whole line.
            # Corrupted lines all seem to be missing # - like that is where they were chopped.
            # remove completely empty lines so can check ...
            data.dropna(axis=0, subset=['temperature'], inplace=True)
            # that the other lines have a hash mark
            data = data.loc[data['temperature'].str.contains('#'), :]

            # CTD files have a hash mark (#) to server time and IP from data.
            # So far, this is always in the temperature field.
            # Strip out that character and convert remaining to a number
            data[start_column] = data[start_column].str.replace('#', '')
            data[start_column] = data[start_column].str.strip().astype(float)
        elif start_column == 'serial_number':  # These are pH files
            # No examples of bad files yet.
            pass
        else:
            logger.error('New format for file. Add instructions on how to read.')

        # ensure that the "time" column has datetime values in UTC
        data["time"] = pd.to_datetime(data["sensor_time"], utc=True)
        data = data[(data['time'] >= start) & (data['time'] <= end)]

        return data

    def get_cals(self, parameter):
        """Retrieve table of calibration coefficients from Google Sheet tab."""
        url = self.calibration_url + self.cal_gids[parameter]
        df = pd.read_excel(url)

        if parameter == 'chlor':
            df['time'] = df['START TIME (UTC)'].apply(
                lambda x: datetime.time.strftime(x, '%H:%M:%S'))
            df['time'] = df['START DATE'].dt.strftime('%m/%d/%Y') + ' ' + df['time']
            df['time'] = pd.to_datetime(df['time'], utc=True)
        elif parameter == 'o2':
            df['time'] = pd.to_datetime(df['START TIME'], utc=True)
        else:
            pass  # no times in pH calibrations

        return df
