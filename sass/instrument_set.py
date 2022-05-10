#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Descriptions of instrument sets."""

import string
import pathlib
import datetime
from io import StringIO

import numpy as np
import pandas as pd
from requests.exceptions import HTTPError
from dateutil.relativedelta import relativedelta

from sass import logger

from . import utilities


class InstrumentSet:
    """Collects the information associated with a set of instrumentation installed at a site."""
    def __init__(self, set_id=None, start_date=None, end_date=None,
                 station_name=None, raw_data_tag=None, proc_data_tag=None, columns=[],
                 calibration_url='', chlor_tab=None, chlor_gid=None,
                 o2_tab=None, o2_gid=None,
                 ph_tab=None, ph_gid=None, ph_salinity_set=None, ip=None, **kwargs):
        """Fills an InstrumentSet with information read from a JSON config file.

        :param set_id: unique identifier of the set (string)
        :param start_date: when the instrumentation was installed (ISO string)
        :param end_date: when the instrumentation was removed (ISO string)
        :param station_id:  where the InstrumentSet was installed (string)
        :param raw_data_tag: indentifier of where data for the InstrumentSet is stored (string)
        :param proc_data_tag: where data will be written, if different (string)
        :param columns: the column header for the raw data (list of strings)
        :param calibration_url: dictionary of Google Sheet url and tab name/uid
        :param chlor_tab: Google sheet tab name for the Fluorometer (string)
        :param chlor_gid: Google sheet id code for the Fluorometer (string)
        :param o2_tab: Google sheet tab name for the Oxygen Sensor (string)
        :param o2_gid: Google sheet id code for the Oxygen Sensor (string)
        :param ph_tab: Google sheet tab name for the SeaFET (string)
        :param ph_gid: Google sheet id code for the SeaFET (string)
        :param ph_salinity_set: set_id of the instrument set that will provide salinity
        :param ip: IP address connects the instrument to each line in the data file (string)
        :param kwargs:
        """
        # basic info like where and when
        self.set_id = set_id
        self.station_name = station_name
        self.ip = ip
        if start_date:
            self.start_date = utilities.parse_datetime(start_date)
        else:
            # if instrument set hasn't started yet, use this to trigger "don't do"
            self.start_date = None
        if end_date:
            self.end_date = utilities.parse_datetime(end_date)
        else:
            # if instrument set hasn't ended, it's going right now
            self.end_date = utilities.parse_datetime(datetime.datetime.now())

        # where reading and writing data - for early years, they are different
        self.raw_data_tag = raw_data_tag
        if proc_data_tag:
            self.proc_data_tag = proc_data_tag
        else:
            self.proc_data_tag = raw_data_tag

        # where to get calibration coefficients
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

        sio scs is whitespace delim but others are comma delim.  pandas should be able to
        sense that difference but it doesn't. had to add a manual check.

        See README.md for notes on how bad data is filtered out.

        :param url: name of a file to process. Was once a URL also.
        :param start: earliest datetime allowed
        :param end: latest datetime allowed
        :return: DataFrame of raw data
        """
        names = self.data_columns
        start_column = names[2]  # skipping fields server time and ip
        if type(url) is pathlib.PosixPath:
            try:
                delim_whitespace = False
                # adding this check for SIO Self-calibrating SeapHOx
                with open(url, encoding="ISO-8859-1") as f:
                    line = f.readline()
                    if ',' not in line:
                        delim_whitespace = True
                data = pd.read_csv(url, names=names, encoding="ISO-8859-1",
                                   delim_whitespace=delim_whitespace)
            except FileNotFoundError:
                # hopefully runner will catch before this
                logger.warn(f"No data found at {url}")
                return pd.DataFrame({})
        else:
            try:
                raw_dataset = utilities.requests_get(url)
            except HTTPError:
                logger.warn(f"No data found at {url}")
                return pd.DataFrame({})

            # No column headers at all here
            data = pd.read_csv(StringIO(raw_dataset), names=names)

        # some incoming files have data from multiple instruments, so filter to just one
        # also filters out 0.0.0.0 except SIO SCS which has ip 0.0.0.0 in its instrument set
        data = data.loc[data['ip'] == self.ip]
        if len(data) == 0:
            return pd.DataFrame({})

        # bad data is non-ascii characters. These are what might reasonably be in a line
        normal = string.digits + string.ascii_letters + string.punctuation + string.whitespace
        try:
            # remove those, and if there is anything left, it's gibberish and a bad line so drop it.
            # gibberish can be in any data cell, so have to test all the columns at once
            cols = data.select_dtypes(object)
            mask = cols.apply(lambda x: ~x.str.strip(normal).astype(bool))
            data = data[mask.all(axis=1)]

            if start_column == 'temperature':  # I think CTD files always start with temperature
                # all remaining lines should have a hash mark
                data = data.loc[data['temperature'].str.contains('#'), :]
                # The only take the numbers in that column - no hash, no gibberish
                data[start_column].replace(regex=True, inplace=True,
                                           to_replace=r'[^0-9.\-]', value=r'')
        except AttributeError:
            # there are a couple files that have good data but no hash marks anywhere
            # so the temperature column is parsed as a float. No need to convert.
            pass

        # some lines are empty after the ip (and hash mark)
        data.replace('', np.nan, inplace=True)
        data.dropna(axis=0, subset=['temperature'], inplace=True)
        if len(data) == 0:
            return pd.DataFrame({})

        # a variation might be to have date and time in separate columns
        if 'sensor_date' in data.columns and 'sensor_time' in data.columns:
            # but if it is, it had better not have times in the date column
            # like SIO "19 Oct 2015 21:50:40"
            data = data.loc[~data['sensor_date'].str.contains(':')]
            # and SIO SCS has its dates like "2022/04/30" so convert that first
            if data['sensor_date'].str.contains('/').all():
                data['tmp_date'] = pd.to_datetime(data['sensor_date'], format="%Y/%m/%d")
                data['sensor_date'] = data['tmp_date'].dt.strftime("%d %b %Y ")
            data['sensor_time'] = data['sensor_date'] + data['sensor_time']
            data.drop(columns=['sensor_date'], inplace=True)

        # It's important there is a value for time and that it look like time
        # (sometimes commas/columns get dropped so this is also a check for that)
        data = data.loc[data['sensor_time'].str.contains(':')]
        if len(data) == 0:
            return pd.DataFrame({})

        data["time"] = pd.to_datetime(data["sensor_time"], utc=True, errors='coerce')
        data.dropna(axis=0, subset=['time'], inplace=True)
        if len(data) == 0:
            return pd.DataFrame({})
        # for the merge with calibration coefficients, make sure data are sorted by time
        data = data.sort_values(by=['time'])
        data.reset_index(drop=True, inplace=True)

        # It's important that these columns are floats
        # There might be some residual letters hanging around, and sets those cells to NoN
        names = ['temperature', 'salinity', 'pressure', 'sigmat', 'conductivity',
                 'O2_raw_voltage', 'O2_phase_delay', 'fluorometer_v',
                 'ph_ext', 'ph_int', 'v_ext', 'v_int']
        names = list(set(names) & set(data.columns))
        cols = data[names].select_dtypes(object)
        data[cols.columns] = cols.apply(lambda x: pd.to_numeric(x, errors='coerce'))

        # clean-up missing O2 values
        data = data.where(data != -9.999)
        data = data.where(data != -0.999)

        return data

    def get_cals(self, parameter):
        """Retrieve table of calibration coefficients from Google Sheet tab.

        For the merge with data, make sure they are sorted by time
        """
        url = self.calibration_url + self.cal_gids[parameter]
        df = pd.read_excel(url)

        if parameter == 'chlor' or parameter == 'o2':
            df['time'] = pd.to_datetime(df['START TIME UTC'], utc=True)
        else:
            pass  # no times in pH calibrations (yet?)

        if 'time' in df.columns:
            df = df.sort_values(by=['time'])
            df.reset_index(drop=True, inplace=True)

        return df
