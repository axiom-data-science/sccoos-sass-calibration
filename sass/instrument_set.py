#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Descriptions of instrument sets."""

from io import StringIO
import pathlib
import datetime

import pandas as pd
from requests.exceptions import HTTPError
from dateutil.relativedelta import relativedelta

from sass import logger
from . import utilities


class InstrumentSet:
    """Collects the information associated with a set of instrumentation installed at a site."""
    def __init__(self, set_id=None, start_date=None, end_date=None,
                 station_name=None, raw_data_tag=None, columns=[], calibration_url='',
                 chlor_tab=None, chlor_gid=None,
                 o2_tab=None, o2_gid=None,
                 ph_tab=None, ph_gid=None, ph_salinity_set=None, **kwargs):
        """Fills an InstrumentSet with information read from a JSON config file.

        :param set_id: unique identifier of the set (string)
        :param start_date: when the instrumentation was installed (ISO string)
        :param end_date: when the instrumentation was removed (ISO string)
        :param station_id:  where the InstrumentSet was installed (string)
        :param raw_data_tag: indentifier of where data for the InstrumentSet is stored (string)
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
        if start_date:
            self.start_date = utilities.parse_datetime(start_date)
        else:
            self.start_date = None  # triggers don't do because the instrument set hasn't started yet
        if end_date:
            self.end_date = utilities.parse_datetime(end_date)
        else:
            self.end_date = utilities.parse_datetime(datetime.datetime.now())

        self.station_name = station_name
        self.raw_data_tag = raw_data_tag
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

    def build_file_list(self, start, end):
        """Build a list of daily files in directories by month.

        :param start: datetime of earliest date
        :param end: datetime of latest date
        :return: list of strings of daily data file names
        """
        files = []
        date = start.date()
        while date <= end.date():
            file_tag = date.strftime('%Y%m%d')
            dir_tag = date.strftime('%Y-%m')
            files.append(f"{self.raw_data_tag}/{dir_tag}/data-{file_tag}.dat")
            date += relativedelta(days=1)

        return files

    def retrieve_and_parse_raw_data(self, url) -> pd.DataFrame:
        """Read raw SASS data from URL and convert it to a DataFrame with headers.

        See README.md for notes on how bad data is filtered out.

        :param url: name of a file to process. Was once a URL also.
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

        # superbad = not even the ip address is right. remove those right away.
        data = data.loc[data['ip'] != '0.0.0.0']

        start_column = names[2]  # skipping fields server time and ip
        if start_column == 'temperature':  # I think CTD files always start with temperature
            # remove completely empty lines so can check ...
            data.dropna(axis=0, subset=['temperature'], inplace=True)
            # that the other lines have a hash mark
            data = data.loc[data['temperature'].str.contains('#'), :]
            # The only take the numbers in that column - no hash, no gibberish
            data[start_column].replace(regex=True, inplace=True, to_replace=r'[^0-9.\-]', value=r'')

            # It's important that these columns are floats
            cols = ['temperature', 'salinity', 'O2_raw_voltage', 'O2_phase_delay', 'V2']
            cols = list(set(cols) & set(data.columns))
            for col in cols:
                data[col] = data[col].astype(float)

        elif start_column == 'serial_number':  # These are pH files
            # No examples of bad files yet.
            pass
        else:
            logger.error('New format for file. Add instructions on how to read.')

        # ensure that the "time" column has datetime values in UTC
        data["time"] = pd.to_datetime(data["sensor_time"], utc=True)

        return data

    def get_cals(self, parameter):
        """Retrieve table of calibration coefficients from Google Sheet tab."""
        url = self.calibration_url + self.cal_gids[parameter]
        df = pd.read_excel(url)

        if parameter == 'chlor':
            # df['time'] = df['START TIME (UTC)'].apply(
            #     lambda x: datetime.time.strftime(x, '%H:%M:%S'))
            # df['time'] = df['START DATE'].dt.strftime('%m/%d/%Y') + ' ' + df['time']
            # df['time'] = pd.to_datetime(df['time'], utc=True)
            try:
                df['time'] = pd.to_datetime(df['START TIME'], utc=True)
            except KeyError:
                df['time'] = pd.to_datetime(df['START TIME UTC'], utc=True)
        elif parameter == 'o2':
            df['time'] = pd.to_datetime(df['START TIME'], utc=True)
        else:
            pass  # no times in pH calibrations

        return df
