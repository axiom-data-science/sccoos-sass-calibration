#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions call the calibration routines with actual data."""

import pandas as pd

from sass import logger
from .seafet_ph import calibrate_ph
from .ctd_chlorophyll import calibrate_chlorophyll
from .sbe63_o2 import calibrate_oxygen, calibrate_temperature


def get_chlor(data, cals):
    """Call the chlorophyll calibration with data and coefficients."""
    # cals.drop(columns=['START TIME', 'START TIME\n(UTC)',
    #                    'SERIAL\nNUMBER', 'CALIBRATION\nDATE'], inplace=True)
    data_all = pd.merge_asof(data, cals, on=['time'], direction='backward')

    data_all.rename(columns={'Clean Water Offset (CWO)': 'clean_water_offset',
                             'Scale Factor': 'scale_factor',
                             'V2': 'output'}, inplace=True)
    data_all = data_all[['output', 'scale_factor', 'clean_water_offset']]
    data_all['chlor_calc'] = data_all.apply(lambda x: calibrate_chlorophyll(**x), axis=1)

    return data_all['chlor_calc'].round(2)


def get_o2(data, cals):
    """Call the O2 calibration with data and coefficients.

    calibrate_temperature(voltage, TA0=None, TA1=None, TA2=None, TA3=None, **kwargs)
    calibrate_oxygen(output, temperature, salinity=0, pressure=0,
                     A0=None, A1=None, A2=None, B0=None, B1=None,
                     C0=None, C1=None, C2=None, E=None, **kwargs)
    """
    # merge the important cali columns with the data to get right calis for dates
    try:
        cals.drop(columns=['START TIME', 'SERIAL NUMBER', 'CALIBRATION DATE'], inplace=True)
    except KeyError:
        pass
    data_all = pd.merge_asof(data, cals, on=['time'], direction='backward')

    # Calculate the O2 sensor temperature (overwrites the CTD temperature)
    data_all.rename(columns={'O2_raw_voltage': 'voltage'}, inplace=True)
    data_all['temperature'] = data_all.apply(lambda x: calibrate_temperature(**x), axis=1)

    # Use the O2 sensor temperature to calculate O2
    data_all.rename(columns={'O2_phase_delay': 'output'}, inplace=True)
    data_all['oxygen_calc'] = data_all.apply(lambda x: calibrate_oxygen(**x), axis=1)

    return data_all['oxygen_calc'].round(2)


def get_ph(data, cals, ctd_data):
    """Call the pH calibration with data and coefficients.
    
    Have to get the data for salinity too
    And calibrations organized by instrument serial number instead of date
    Sensor,Kext0,Kext2,Kint0,Kint2
    TODO: Have them reorganize pH coeffs by date
    """
    # Which instrument?
    instrument = data['serial_number'].unique()  # i.e. SEAFET02145
    if len(instrument) != 1:
        logger.error('More than one instrument in file.  Fix code.')
    instrument = int(instrument[0].replace('SEAFET', ''))

    # Prep data
    data_all = data[['time', 'v_ext', 'temperature']].copy()
    data_all.rename(columns={'v_ext': 'voltage'}, inplace=True)

    # transfer those calibration coefficients into data
    cal = cals.loc[cals['Sensor'].astype(int) == instrument]
    data_all['k0'] = cal['Kext0'].values[0]
    data_all['k2'] = cal['Kext2'].values[0]

    # interpolate salinity to times with voltage
    ctd_data = ctd_data[['time', 'salinity']]
    data_all = data_all.merge(ctd_data, on=['time'], how='outer')
    data_all.sort_values(by=['time'], inplace=True)
    data_all.set_index('time', inplace=True)
    data_all['salinity'] = data_all['salinity'].interpolate()
    data_all['salinity'] = data_all['salinity'].fillna(method="ffill")
    data_all['salinity'] = data_all['salinity'].fillna(method="bfill")
    data_all.dropna(subset=['voltage'], inplace=True)
    data_all.reset_index(drop=False, inplace=True)

    data_all['calc_ph'] = data_all.apply(lambda x: calibrate_ph(**x, external=True), axis=1)
    return data_all['calc_ph'].round(2)
