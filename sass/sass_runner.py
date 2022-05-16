#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions to establish the processing pathway."""

import json
from pathlib import Path

from sass import logger, instrument_set

from .calibrations import get_o2, get_ph, get_chlor

here = Path(__file__).parent
instrument_set_filename = 'config/instrument_sets.json'
incoming = '../data/incoming/'
outgoing = '../data/calibrated/'


def load_configs(path_to_file, set=None):
    """Read a configuration file into a dictionary then build InstrumentSets.

    :param path_to_file: Posix path to JSON configuration file
    :param set: optional set_id to match
    :return: a list of instruments sets. Either all or just the one that matches
    """
    with open(str(path_to_file), "r") as f:
        config_dict = json.loads(f.read())
    configs = []
    for config in config_dict['sets']:
        configs.append(instrument_set.InstrumentSet(**config))

    if set:  # take a subset
        configs = [s for s in configs if s.set_id == set]

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
        logger.info(f'{start.date()} to {end.date()} for instrument set {set_id}')
        # Get the instrument configuration
        path = here.joinpath(instrument_set_filename)
        configs = load_configs(path, set=set_id)
        if len(configs) == 0:
            logger.error(f'****  {set_id} is not defined in instrument_set.json ****')
            logger.error('Job failed.')
            return 1
        else:
            this_set = configs[0]

        # check those dates and build the list of files
        if not this_set.start_date:
            logger.error(f'{this_set.set_id} is not active yet. '
                         'Set start_date in instrument_set.json and try again.')
            logger.error('Job failed.')
            return 1
        if end < this_set.start_date or start > this_set.end_date:
            logger.error(f'{this_set.set_id} is not active during the time you requested.')
            logger.error('Job failed.')
            return 1
        start = max(start, this_set.start_date)
        end = min(end, this_set.end_date)
        logger.info(f'Adjusted: {start.date()} to {end.date()} for instrument set {set_id}')
        logger.info(this_set)
        files = this_set.build_file_list(start, end)

        # If doing pH, then also need salinity from the CTD. Don't do it if can't find it.
        salinity_set = instrument_set.InstrumentSet(set_id='Empty')
        if 'ph' in this_set.parameters:
            if this_set.ph_salinity_set:
                configs = load_configs(path, set=this_set.ph_salinity_set)
                if len(configs) == 0:
                    logger.error('For pH, must include where to get salinity. But can not find '
                                 f'the {this_set.ph_salinity_set}. Just copying files without '
                                 'pH adjustment.')
                    this_set.parameters.remove('ph')
                else:
                    salinity_set = configs[0]
                logger.debug(salinity_set)
            else:
                logger.error('For pH, must include where to get salinity. Set ph_salinity_set in '
                             'instrument_set.json. Just copying files without pH adjustment.')
                this_set.parameters.remove('ph')

        # read and stash the calibration coeffs
        # TODO maybe switch to reading local, pre-grabbed coeffs?
        cals = {}
        for parameter in this_set.parameters:
            logger.info(f'Getting calibration coefficients for {parameter}')
            df_cal = this_set.get_cals(parameter)
            cal_filename = f'{incoming}cals/{this_set.set_id}_{parameter}.csv'
            path = here.joinpath(cal_filename)
            df_cal.to_csv(path, index=False)
            cals[parameter] = df_cal

        for file in files:
            path = here.joinpath(incoming + file)
            if not path.exists():
                logger.debug(f"No {file}. Skipping...")
                continue
            logger.debug(f'Reading {path}')
            data = this_set.retrieve_and_parse_raw_data(path)
            if len(data) == 0:
                logger.debug("no data")
                continue

            for parameter in this_set.parameters:
                df_cal = cals[parameter]
                if parameter == 'chlor':
                    data['chlor'] = get_chlor(data, df_cal)
                if parameter == 'o2':
                    data['o2'] = get_o2(data, df_cal)
                if parameter == 'ph':
                    # also read the accompanying CTD file for salinity
                    ctd_file = file.replace(this_set.raw_data_tag, salinity_set.raw_data_tag)
                    ctd_path = here.joinpath(incoming + ctd_file)
                    if not ctd_path.exists():
                        logger.debug(f"No {ctd_file}. Cannot calibrate pH ...")
                        continue
                    logger.debug(f'Reading {ctd_path}')
                    ctd_data = salinity_set.retrieve_and_parse_raw_data(ctd_path)
                    if len(ctd_data) == 0:
                        continue

                    data.dropna(subset=['v_ext'], inplace=True)
                    data['corrected_ph'] = get_ph(data, df_cal, ctd_data)

            # write it out - whether successfully created calibrated values or not
            outfile = file.replace(this_set.raw_data_tag, this_set.proc_data_tag)
            # reset sio-scs-2022 weird filename to what all the others are
            outfile = outfile.replace("data_", "data-")
            path = here.joinpath(outgoing + outfile)
            logger.debug(f'Writing to {str(path)}')
            if not path.parents[0].exists():
                path.parents[0].mkdir(parents=True)
            data.drop(columns=['time'], inplace=True)  # don't need this
            data.to_csv(path, index=False, na_rep='NaN')

        logger.info("All done!")
        return None
