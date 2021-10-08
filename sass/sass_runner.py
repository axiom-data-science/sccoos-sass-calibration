#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions to establish the processing pathway."""

import json
from pathlib import Path

from sass import logger, instrument_set
from .calibrations import get_o2, get_chlor, get_ph

here = Path(__file__).parent
stations_filename = 'config/stations.json'
instrument_set_filename = 'config/instrument_sets.json'
incoming = '../data/incoming'
outgoing = '../data/outgoing'


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
        urls = this_set.build_urls(start, end)

        # If doing pH, then also need salinity from the CTD
        salinity_set = instrument_set.InstrumentSet(set_id='Empty')
        if 'ph' in this_set.parameters:
            salinity_set = next(s for s in instrument_sets if s.set_id == this_set.ph_salinity_set)
            logger.debug(salinity_set)

        # read and stash the calibration coeffs
        # TODO maybe switch to reading local, pre-grabbed coeffs?
        cals = {}
        for parameter in this_set.parameters:
            logger.info(f'Getting calibration coefficients for {parameter}')
            df_cal = this_set.get_cals(parameter)
            cal_filename = f'{incoming}/cals/{this_set.set_id}_{parameter}.csv'
            path = here.joinpath(cal_filename)
            df_cal.to_csv(path, index=False)
            cals[parameter] = df_cal

        for url in urls:
            path = here.joinpath(url.replace('https://sccoos.org/dr/data', incoming))
            if not path.exists():
                continue
            logger.debug(f'Reading {path}')
            data = this_set.retrieve_and_parse_raw_data(path, start, end)
            if len(data) == 0:
                continue

            for parameter in this_set.parameters:
                df_cal = cals[parameter]
                if parameter == 'chlor':
                    data['chlor'] = get_chlor(data, df_cal)
                if parameter == 'o2':
                    data['o2'] = get_o2(data, df_cal)
                if parameter == 'ph':
                    # also read the accompanying CTD file for salinity
                    ctd_url = url.replace(this_set.raw_data_url, salinity_set.raw_data_url)
                    ctd_path = here.joinpath(ctd_url.replace('https://sccoos.org/dr/data',
                                                             incoming))
                    if not ctd_path.exists():
                        continue
                    logger.debug(f'Reading {ctd_path}')
                    ctd_data = salinity_set.retrieve_and_parse_raw_data(ctd_path, start, end)
                    if len(ctd_data) == 0:
                        continue

                    data.dropna(subset=['v_ext'], inplace=True)
                    data['corrected_ph'] = get_ph(data, df_cal, ctd_data)

            # write it out
            path = here.joinpath(url.replace('https://sccoos.org/dr/data', outgoing))
            logger.debug(f'Writing to {str(path)}')
            if not path.parents[0].exists():
                path.parents[0].mkdir(parents=True)
            data.drop(columns=['time'], inplace=True)  # don't need this
            data.to_csv(path, index=False, na_rep='NaN')
