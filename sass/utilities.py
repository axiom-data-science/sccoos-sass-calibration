#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Various helpful routines from packrat and other stuff."""

import math

import requests
from dateutil import tz, parser


def requests_get(url, timeout_seconds=20, encoding='UTF-8',
                 result_type='text', headers=None, auth=None,
                 params=None):
    """Wrapper for get method that might convert response into JSON.

    :param url: what to get (url string)
    :param timeout_seconds: int
    :param encoding: string
    :param result_type: could be 'text' or 'json'
    :param headers: optional header if needed
    :param auth: optional authentication if needed
    :param params: optional additional parameters if needed
    :return:
    """
    # logger.debug(f'GET {url}')
    headers = headers or {}
    response = requests.get(url, timeout=timeout_seconds, allow_redirects=True, headers=headers,
                            auth=auth, params=params)
    response.encoding = encoding
    if response.status_code != 200:
        message = f"GET {response.url}: HTTP {response.status_code}: {response.text}"
        # logger.error(message)
        raise requests.exceptions.HTTPError(message)
    if result_type == 'json':
        return response.json()
    return response.text


def parse_datetime(datestr, tzoffsethrs=0):
    """Parse an ISO date string into datetime with timezone.

    :param datestr: ISO formatted string representation of date
    :param tzoffsethrs: timezone code
    :return:
    """
    if datestr is None:
        return None
    tzoffset_str = ('+' if tzoffsethrs >= 0 else '-') + str(abs(tzoffsethrs))
    return parser.parse(f'{datestr} {tzoffset_str}').astimezone(tz.tzutc())


def proper_rounding(n, ndigits):
    """Round so that something that ends with 5 always goes up.

    "Python 3 rounds according to the IEEE 754 standard, using a round-to-even approach."
    That means that 2.5 rounds to 2.0. Some tests in this package are comparing values
    with few decimal places that were read from a file with calculated values with many
    decimal places. Default Python round() gives inconsistent results, so use this instead.

    Found in https://stackoverflow.com/questions/18473563/
    python-incorrect-rounding-with-floating-point-numbers

    :param n: the number to round
    :param ndigits: how many digits to round too
    :return: the rounded number
    """
    part = n * 10 ** ndigits
    delta = part - int(part)
    # always round "away from 0"
    if delta >= 0.5 or -0.5 < delta <= 0:
        part = math.ceil(part)
    else:
        part = math.floor(part)
    return part / (10 ** ndigits)
