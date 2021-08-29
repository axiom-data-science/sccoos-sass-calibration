from pathlib import Path
from sass.utilities import parse_datetime
from sass.instrument_set import InstrumentSet
import pytest
import responses
import re


here = Path(__file__).parent


@pytest.fixture
def instrumentset():
    return InstrumentSet()


# @pytest.fixture - when actually have stations, use this or something
# def station_sio():
#     return 'sio'


@pytest.fixture
def mocked_responses():
    # Use to mock calls to requests library
    # https://github.com/getsentry/responses
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


def test_url_builder(instrumentset):  # , station_sio):
    """Verify that the collector asks for all the urls we need."""

    # one url
    start = parse_datetime("2021-08-26T03:00:00Z")
    end = parse_datetime("2021-08-26T09:00:00Z")

    urls = instrumentset._build_urls('data', start, end)

    assert "https://sccoos.org/dr/data/data/2021-08/data-20210826.dat" in urls
    assert len(urls) == 1

    # 10 urls
    start = parse_datetime("2021-07-27T03:00:00Z")
    end = parse_datetime("2021-08-5T09:00:00Z")

    urls = instrumentset._build_urls('data', start, end)

    assert "https://sccoos.org/dr/data/data/2021-07/data-20210729.dat" in urls
    assert len(urls) == 10


def test_retrieve_observations(instrumentset, mocked_responses):  # station_sio
    """ Verify that we're reading raw data correctly. """

    # instead of making GET request to the HTTP server, we are going to read a local file
    path = here.joinpath('resources/raw_data/sio_data-20210826.dat')
    with open(path, 'r', encoding='UTF-8') as myfile:
        raw_dataset = myfile.read()

    # this is where GET is mocked (though the GET itself is in the InstrumentSet)
    mocked_responses.add(responses.GET, re.compile(r'.*'), body=raw_dataset)

    start = parse_datetime("2021-08-26T03:00:00Z")
    end = parse_datetime("2021-08-26T05:00:00Z")

    data = instrumentset.retrieve_observations('data', start, end)
    assert len(data) == 30
    assert data['temperature'].iloc[0] == 19.5426
    assert data['time'].iloc[0] == parse_datetime("2021-08-26T03:02:20")


def test_retrieve_corrupt_observations(instrumentset, mocked_responses):  # station_sio
    """ Verify that we're reading raw data correctly even when data are corrupted.
    The corrupted file is real, but I added a empty temperature fields to duplicated another
    error I got later.  That's ",," in the temperature field that was causing the check for
    "#" to balk. """

    # instead of making GET request to the HTTP server, we are going to read a local file
    path = here.joinpath('resources/raw_data/stearns_data-20210720_corrupt.dat')
    with open(path, 'r', encoding='UTF-8') as myfile:
        raw_dataset = myfile.read()

    # this is where GET is mocked (though the GET itself is in the InstrumentSet)
    mocked_responses.add(responses.GET, re.compile(r'.*'), body=raw_dataset)

    start = parse_datetime("2021-07-20T00:00:00Z")
    end = parse_datetime("2021-07-21T00:00:00Z")

    data = instrumentset.retrieve_observations('stearns_wharf', start, end)
    assert len(data) == 78  # 83 lines with 5 corrupt
    assert data['temperature'].iloc[77] ==  16.2690
    assert data['time'].iloc[77] == parse_datetime("2021-07-20T07:41:05")
