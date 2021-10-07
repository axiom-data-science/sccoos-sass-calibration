#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions to establish the processing pathway."""

import json
from pathlib import Path

from sass import logger, instrument_set
from .calibrations import get_chlor, get_ph, get_o2

here = Path(__file__).parent
stations_filename = 'config/stations.json'
instrument_set_filename = 'config/instrument_sets.json'
incoming = '../data/incoming'


def load_configs(path_to_file):
    """Read a configuration file into a dictionary then built InstrumentSets.

    :param path_to_file: Posix path to JSON configuration file
    :return:
    """
    with open(str(path_to_file), "r") as f:
        config_dict = json.loads(f.read())
    configs = []
    for config in config_dict['sets']:
        configs.append(instrument_set.InstrumentSet(**config))

    return configs


class SassCalibrationRunner:
    """Run the processing pipeline."""

    def run(self, start=None, end=None, set_id=None):
        """Run the processing.

        :param start: datetime for first data to be processed
        :param end: Datetime for last data to be processed
        :param set_id: unique identifier for set of instruments to be processed
        :return:
        """
        logger.info(f'{start} to {end} for instrument set {set_id}')
        path = here.joinpath(instrument_set_filename)
        instrument_sets = load_configs(path)
        this_set = next(s for s in instrument_sets if s.set_id == set_id)
        logger.debug(this_set)

        for parameter in this_set.parameters:
            df_cal = this_set.get_cals(parameter)
            cal_filename = f'{incoming}/cals/{this_set.set_id}_{parameter}.csv'
            path = here.joinpath(cal_filename)
            df_cal.to_csv(path, index=False)

            urls = this_set.build_urls(start, end)
            for url in urls:
                data = this_set.retrieve_and_parse_raw_data(url, start, end)
            #     if parameter == 'chlor':
            #         data['chlor'] = get_chlor(data, df_cal)
