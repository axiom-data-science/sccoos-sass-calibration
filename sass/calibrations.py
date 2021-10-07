#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions call the calibration routines with actual data."""

from .seafet_ph import calibrate_ph
from .ctd_chlorophyll import calibrate_chlorophyll
from .sbe63_o2 import calibrate_oxygen, calibrate_temperature


def get_chlor(data, cals):
    """Call the chlorophyll calibration with data and coefficients."""
    # calibrate_chlorophyll(output, scale_factor=None, clean_water_offset=None, **kwargs)
    pass


def get_o2(data, cals):
    """Call the O2 calibration with data and coefficients

    calibrate_temperature(voltage, ta0, ta1, ta2, ta3, **kwargs)
    calibrate_oxygen(output, temperature, salinity=0, pressure=0,
                     A0=None, A1=None, A2=None, B0=None, B1=None,
                     C0=None, C1=None, C2=None, E=None, **kwargs)
    """
    pass


def get_ph(data,cals):

    # calibrate_ph(voltage, temperature, salinity=0, external=False, k0=None, k2=None, **kwargs):
    pass
