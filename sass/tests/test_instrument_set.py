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
    this_set = [s for s in instrument_sets if s.set_id == 'sio-ctd-2016']
    return this_set[0]


@pytest.fixture
def np_set_old():
    """Create an InstrumentSet from JSON file defined above."""
    path = here.joinpath(instrument_set_filename)
    instrument_sets = load_configs(path)
    this_set = [s for s in instrument_sets if s.set_id == 'np-ctd-2013']
    return this_set[0]


@pytest.fixture
def np_set():
    """Create an InstrumentSet from JSON file defined above."""
    path = here.joinpath(instrument_set_filename)
    instrument_sets = load_configs(path)
    this_set = [s for s in instrument_sets if s.set_id == 'np-ctd-2016b']
    return this_set[0]


@pytest.fixture
def sw_set():
    """Create an InstrumentSet from JSON file defined above."""
    path = here.joinpath(instrument_set_filename)
    instrument_sets = load_configs(path)
    this_set = [s for s in instrument_sets if s.set_id == 'sw-ctd-2018']
    return this_set[0]


@pytest.fixture
def np_ph_set():
    """Create an InstrumentSet from JSON file defined above."""
    path = here.joinpath(instrument_set_filename)
    instrument_sets = load_configs(path)
    this_set = [s for s in instrument_sets if s.set_id == 'np-ph-2020']
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


def test_retrieve_old_observations(np_set_old):
    """Verify reading raw data correctly.

    :param np_set_old: a pre-filled InstrumentSet for a file when all are together
    :return:
    """
    # instead of making GET request to the HTTP server, we are going to read a local file
    path = here.joinpath('resources/raw_data/data-20131115_trimmed.dat')

    data = np_set_old.retrieve_and_parse_raw_data(path)
    assert len(data) == 4
    assert data.iloc[0, 2] == 18.3637  # temperature
    # time was added as the last column
    assert data.iloc[0, -1] == parse_datetime("2013-11-15T00:01:29")


def test_retrieve_no_hash(sio_set):
    """Verify reading raw data correctly.

    :param sio_set: a pre-filled InstrumentSet
    :return:
    """
    # instead of making GET request to the HTTP server, we are going to read a local file
    path = here.joinpath('resources/raw_data/data-20170117_no_hash.dat')

    data = sio_set.retrieve_and_parse_raw_data(path)
    assert len(data) == 5
    assert data.iloc[0, 2] == 15.0347  # temperature
    # time was added as the last column
    assert data.iloc[0, -1] == parse_datetime("2017-01-27T00:00:06")


def test_retrieve_corrupt_observations(sw_set):
    """Verify correct reading of raw data even when data are corrupted.

    The corrupted file is real, but I added a empty temperature fields to duplicate another
    error I got later.  That's ",," in the temperature field that was causing the check for
    "#" to balk.

    :param sio_set: a pre-filled InstrumentSet
    :return:
    """
    # instead of making GET request to the HTTP server, we are going to read a local file
    path = here.joinpath('resources/raw_data/stearns_data-20210720_corrupt.dat')

    data = sw_set.retrieve_and_parse_raw_data(path)
    assert len(data) == 78  # 83 lines with 5 corrupt
    assert data['temperature'].iloc[77] == 16.2690
    assert data['time'].iloc[77] == parse_datetime("2021-07-20T07:41:04")


def test_retrieve_superbad_observations(sw_set):
    """Verify correct reading of raw data even when data are corrupted.

    This corrupted file is real - no alterations.  Just super gross.

    :param sio_set: a pre-filled InstrumentSet
    :return:
    """
    # instead of making GET request to the HTTP server, we are going to read a local file
    path = here.joinpath('resources/raw_data/stearns_data-20211014_superbad.dat')

    data = sw_set.retrieve_and_parse_raw_data(path)
    # this file started with 323 lines but only 90 are good.  Told you it was appalling.
    assert len(data) == 90

    # This one is even worse! and it has gibberish in an otherwise fine temperature entry
    path = here.joinpath('resources/raw_data/stearns_data-20211010_superbad.dat')

    data = sw_set.retrieve_and_parse_raw_data(path)
    # this file started with 358 lines but only 43 are good. One more removed because I
    # can't be sure temperature in a corrupted filed is good.
    assert len(data) == 42


def test_retrieve_superbad_withhash(np_set):
    """Verify correct reading of raw data even when data are corrupted.

    These corrupted files are real - no alterations.  Just super gross.

    :param np_set: a pre-filled InstrumentSet
    :return:
    """
    # This one had a hash sign in amongst the gibberish
    path = here.joinpath('resources/raw_data/newport_data-20210226_badwhash.dat')

    data = np_set.retrieve_and_parse_raw_data(path)
    # again very few have useable data.
    assert len(data) == 5

    # This one is all gibberish
    path = here.joinpath('resources/raw_data/newport_data-20210227_worst.dat')

    data = np_set.retrieve_and_parse_raw_data(path)
    # again very few have useable data.
    assert len(data) == 1


def test_retrieve_bad_ph(np_ph_set):
    """Verify correct reading of raw data even when data are corrupted.

    These corrupted files are real - no alterations.  Just super gross.

    :param np_ph_set: a pre-filled InstrumentSet
    :return:
    """
    # This one had a hash sign in amongst the gibberish
    path = here.joinpath('resources/raw_data/newport_ph_data-20210110_corrupt.dat')

    data = np_ph_set.retrieve_and_parse_raw_data(path)
    # 2 bad lines - one with garbage and the other truncated before time.
    assert len(data) == 33
