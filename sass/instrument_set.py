"""
This is a reST style.

:param param1: this is a first param
:param param2: this is a second param
:returns: this is a description of what is returned
:raises keyError: raises an exception
"""

import pandas as pd
from requests.exceptions import HTTPError
from io import StringIO
from dateutil.relativedelta import relativedelta
from sass import utilities


class InstrumentSet:
    def __init__(self, id, associationType, foreignName, foreignUrl, agent=None, agentId=None, **kwargs):
        self.id = id
        self.associationType = associationType
        self.foreignName = foreignName
        self.foreignUrl = foreignUrl
        self.agent = None
        if agentId:
            self.agent = Agent(id=agentId)
        if agent:
            self.agent = _model_obj(agent, Agent)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'StationAgent{{type={self.associationType},agent={self.agent}}}'

    # urls are split by date at the source
    # there are no headers at the source

    def __init__(self):
        self.url_base = 'https://sccoos.org/dr/data/'
        # each site has a different CSV file format - without headers!  So track them here.
        self.column_names = {
        }


    def retrieve_observations(self, station_code, start, end) -> list:
        """Build urls for one variable at a time, then smash them together and convert to feeds."""

        all_data = pd.DataFrame({})
        urls = self._build_urls(station_code, start, end)
        for url in urls:
            data = self.retrieve_and_parse_observations(url, station_code, start, end)
            all_data = all_data.append(data)

        return all_data  # type: pd.DataFrame

    def retrieve_and_parse_observations(self, url, station_code, start, end) -> list:
        """Take in a list of urls and send back a one column dataframe with datetimeindex
        """

        try:
            raw_dataset = utilities.requests_get(url)
        except HTTPError:
            # logger.warn(f"No data found for {station.foreignId} at {url}")
            return []

        # No column headers at all here
        names = self.column_names[station_code]
        data = pd.read_csv(StringIO(raw_dataset), names=names)

        # There are some corrupted lines that have only a subset of fields.
        # Who knows which fields remain so drop the whole line.
        # Corrupted lines all seem to be missing # - like that is where they were chopped.
        data.dropna(axis=0, subset=['temperature'], inplace=True)  # remove completely empty so can check ...
        data = data.loc[data['temperature'].str.contains('#'), :]  # that line has a hash mark

        # Files have a hash mark (#) to indicate the beginning of the data after date and IP.
        start_column = names[2]
        # So far, this is always temperature. If it isn't, I want to know.  Think about it when it happens
        assert start_column == 'temperature'
        # Strip out that character and convert remaining to a number
        data[start_column] = data[start_column].str.replace('#', '')
        data[start_column] = data[start_column].str.strip().astype(float)

        # ensure that the "time" column has datetime values in UTC
        data["time"] = pd.to_datetime(data["date"])
        data = data[(data['time'] >= start) & (data['time'] <= end)]

        return data

    def _build_urls(self, station_code, start, end):
        """ Build a list of urls. Daily files, in directories by month """

        urls = []

        date = start
        while date < end:
            file_tag = date.strftime('%Y%m%d')
            dir_tag = date.strftime('%Y-%m')
            urls.append(
                self.url_base +
                f"{station_code}" + "/"
                f"{dir_tag}" + "/"
                f"data-{file_tag}.dat"
            )
            date += relativedelta(days=1)

        return urls
