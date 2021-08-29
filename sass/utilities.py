"""

    Various helpful routines from packrat

"""

import requests
from datetime import datetime
from dateutil import parser, tz


def requests_get(url, timeout_seconds=20, encoding='UTF-8', result_type='text', headers=None, auth=None,
                 params = None):
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

