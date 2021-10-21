#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test usages of InstrumentSet class and methods."""

from pathlib import Path

import pytest

from ..sass_runner import load_configs
from ..utilities import parse_datetime

here = Path(__file__).parent
instrument_set_filename = '../config/instrument_sets.json'


@pytest.fixture
def sio_set():
    """Create an InstrumentSet from JSON file defined above."""
    path = here.joinpath(instrument_set_filename)
    instrument_sets = load_configs(path)
    this_set = [s for s in instrument_sets if s.station_name == 'Scripps Pier']
    return this_set[0]


@pytest.fixture
def np_set():
    """Create an InstrumentSet from JSON file defined above."""
    path = here.joinpath(instrument_set_filename)
    instrument_sets = load_configs(path)
    this_set = [s for s in instrument_sets if s.set_id == 'np-ctd-2021']
    return this_set[0]


def test_file_list(sio_set):
    """Verify that the collector asks for all the files we need.

    :param sio_set: a pre-filled InstrumentSet
    :return:
    """
    # one file - no partial days
    start = parse_datetime("2021-08-26T00:00:00Z")
    end = parse_datetime("2021-08-26T00:00:00Z")

    files = sio_set.build_file_list(start, end)

    assert "scripps_pier/2021-08/data-20210826.dat" in files
    assert len(files) == 1

    # 10 files
    start = parse_datetime("2021-07-27T00:00:00Z")
    end = parse_datetime("2021-08-05T00:00:00Z")

    files = sio_set.build_file_list(start, end)

    assert "scripps_pier/2021-07/data-20210729.dat" in files
    assert len(files) == 10


def test_retrieve_observations(sio_set):
    """Verify reading raw data correctly.

    :param sio_set: a pre-filled InstrumentSet
    :param mocked_responses: mock Get so retrieves local file
    :return:
    """
    # instead of making GET request to the HTTP server, we are going to read a local file
    path = here.joinpath('resources/raw_data/sio_data-20210826.dat')

    start = parse_datetime("2021-08-26T03:00:00Z")
    end = parse_datetime("2021-08-26T05:00:00Z")

    data = sio_set.retrieve_and_parse_raw_data(path)
    data = data[(data['time'] >= start) & (data['time'] <= end)]  # check that time makes sense
    assert len(data) == 30
    assert data.iloc[0, 2] == 19.5426  # temperature
    # time was added as the last column
    assert data.iloc[0, -1] == parse_datetime("2021-08-26T03:02:18")


def test_retrieve_corrupt_observations(sio_set):
    """Verify correct reading of raw data even when data are corrupted.

    The corrupted file is real, but I added a empty temperature fields to duplicate another
    error I got later.  That's ",," in the temperature field that was causing the check for
    "#" to balk.

    :param sio_set: a pre-filled InstrumentSet
    :param mocked_responses: mock Get so retrieves local file
    :return:
    """
    # instead of making GET request to the HTTP server, we are going to read a local file
    path = here.joinpath('resources/raw_data/stearns_data-20210720_corrupt.dat')

    data = sio_set.retrieve_and_parse_raw_data(path)
    assert len(data) == 78  # 83 lines with 5 corrupt
    assert data['temperature'].iloc[77] == 16.2690
    assert data['time'].iloc[77] == parse_datetime("2021-07-20T07:41:04")


def test_retrieve_superbad_observations(sio_set):
    """Verify correct reading of raw data even when data are corrupted.

    This corrupted file is real - no alterations.  Just super gross.

    :param sio_set: a pre-filled InstrumentSet
    :param mocked_responses: mock Get so retrieves local file
    :return:
    """
    # instead of making GET request to the HTTP server, we are going to read a local file
    path = here.joinpath('resources/raw_data/stearns_data-20211014_superbad.dat')

    data = sio_set.retrieve_and_parse_raw_data(path)
    # this file started with 323 lines but only 90 are good.  Told you it was appalling.
    assert len(data) == 90

    # This one is even worse! and it has gibberish in an otherwise fine temperature entry
    path = here.joinpath('resources/raw_data/stearns_data-20211010_superbad.dat')

    data = sio_set.retrieve_and_parse_raw_data(path)
    # this file started with 358 lines but only 43 are good.
    assert len(data) == 43


def test_retrieve_superbad_withhash(np_set):
    """Verify correct reading of raw data even when data are corrupted.

    This corrupted file is real - no alterations.  Just super gross.

    :param np_set: a pre-filled InstrumentSet
    :param mocked_responses: mock Get so retrieves local file
    :return:
    """
    # This one had a hash sign in amongst the gibberish
    path = here.joinpath('resources/raw_data/newport_data-20210226_badwhash.dat')

    data = np_set.retrieve_and_parse_raw_data(path)
    # again very few have useable data.
    assert len(data) == 5
