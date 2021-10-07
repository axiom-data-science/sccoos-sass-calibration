#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions call the calibration routines with actual data."""

import pandas as pd

# from .seafet_ph import calibrate_ph
# from .ctd_chlorophyll import calibrate_chlorophyll
from .sbe63_o2 import calibrate_oxygen, calibrate_temperature


def get_chlor(data, cals):
    """Call the chlorophyll calibration with data and coefficients."""
    cals.drop(columns=['START TIME', 'START TIME (UTC)',
                       'SERIAL NUMBER', 'CALIBRATION DATE'], inplace=True)
    data_all = pd.merge_asof(data, cals, on=['time'], direction='backward')

    data_all.rename(columns={'Clean Water Offset (CWO)': 'clean_water_offset',
                             'Scale Factor': 'scale_factor'}, inplace=True)
    # calibrate_chlorophyll(output, scale_factor=None, clean_water_offset=None, **kwargs)
    pass


def get_o2(data, cals):
    """Call the O2 calibration with data and coefficients.

    calibrate_temperature(voltage, TA0=None, TA1=None, TA2=None, TA3=None, **kwargs)
    calibrate_oxygen(output, temperature, salinity=0, pressure=0,
                     A0=None, A1=None, A2=None, B0=None, B1=None,
                     C0=None, C1=None, C2=None, E=None, **kwargs)
    """
    # merge the important cali columns with the data to get right calis for dates
    cals.drop(columns=['START TIME', 'SERIAL NUMBER', 'CALIBRATION DATE'], inplace=True)
    data_all = pd.merge_asof(data, cals, on=['time'], direction='backward')

    # Calculate the O2 sensor temperature (overwrites the CTD temperature)
    data_all.rename(columns={'O2_raw_voltage': 'voltage'}, inplace=True)
    data_all['temperature'] = data_all.apply(lambda x: calibrate_temperature(**x), axis=1)

    # Use the O2 sensor temperature to calculate O2
    data_all.rename(columns={'O2_phase_delay': 'output'}, inplace=True)
    data_all['oxygen_calc'] = data_all.apply(lambda x: calibrate_oxygen(**x), axis=1)

    return data_all['oxygen_calc'].round(2)


def get_ph(data, cals):
    """Call the pH calibration with data and coefficients."""
    # calibrate_ph(voltage, temperature, salinity=0, external=False, k0=None, k2=None, **kwargs):
    pass
