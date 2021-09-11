"""

    Various helpful routines from packrat and other stuff

"""

import requests
import math
from dateutil import parser, tz


def requests_get(url, timeout_seconds=20, encoding='UTF-8', result_type='text', headers=None, auth=None,
                 params=None):
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
    if datestr is None:
        return None
    # TODO: tests
    # TODO: is there a better way to do this?
    tzoffset_str = ('+' if tzoffsethrs >= 0 else '-') + str(abs(tzoffsethrs))
    return parser.parse(f'{datestr} {tzoffset_str}').astimezone(tz.tzutc())


def proper_rounding(n, ndigits):
    """ Round so that something that ends with 5 always goes up
    "Python 3 rounds according to the IEEE 754 standard, using a round-to-even approach."
    That means that 2.5 rounds to 2.0. Some tests in this package are comparing values with few decimal places
    that were read from a file with calculated values with many decimal places. Default Python round() gives
    inconsistent results, so use this instead.

    :param n: the number to round
    :param ndigits: how many digits to round too
    :return: the rounded number

    Found in https://stackoverflow.com/questions/18473563/python-incorrect-rounding-with-floating-point-numbers
    """
    part = n * 10 ** ndigits
    delta = part - int(part)
    # always round "away from 0"
    if delta >= 0.5 or -0.5 < delta <= 0:
        part = math.ceil(part)
    else:
        part = math.floor(part)
    return part / (10 ** ndigits)
