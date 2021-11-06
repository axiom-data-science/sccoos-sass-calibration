#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test bits of sass_runner class and methods."""

from pathlib import Path

import pytest

from ..utilities import parse_datetime
from ..sass_runner import load_configs, SassCalibrationRunner

here = Path(__file__).parent
instrument_set_filename = '../config/instrument_sets.json'


@pytest.fixture
def sio_set():
    """Create an sass runner file defined above."""
    path = here.joinpath(instrument_set_filename)
    instrument_sets = load_configs(path)
    this_set = [s for s in instrument_sets if s.station_name == 'Scripps Pier']
    return this_set[0]


def test_no_set_id():
    """Right response if the set doesn't exist."""
    start = parse_datetime("2021-07-27T00:00:00Z")
    end = parse_datetime("2021-08-05T00:00:00Z")
    runner = SassCalibrationRunner()
    code = runner.run(start=start, end=end, set_id='foo')
    assert code == 1


def test_bad_dates():
    """Right response if the dates are out of bounds."""
    start = parse_datetime("2002-07-27T00:00:00Z")
    end = parse_datetime("2002-07-27T00:00:00Z")
    runner = SassCalibrationRunner()
    assert 1 == runner.run(start=start, end=end, set_id='sio-ctd-2021')

    start = parse_datetime("2102-07-27T00:00:00Z")
    end = parse_datetime("2102-07-27T00:00:00Z")
    runner = SassCalibrationRunner()
    assert 1 == runner.run(start=start, end=end, set_id='sio-ctd-2021')
