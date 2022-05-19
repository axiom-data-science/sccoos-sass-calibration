#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Define the equations that calibrate O2 from Aanderaa Optode.

The self calibrating SeapHOx installed at the Scripps Pier in 2022 includes an
Aanderaa instrument for measuring Oxygen. The model number is 5730.
The instrument reports "O2con", "O2sat", and "O2temp", meaning that the raw
voltages have already been converted.

However, these values still need to be corrected for salinity and pressure. I have
two references for this calculation.
* https://www.aanderaa.com/media/pdfs/oxygen-optode-4330-4835-and-4831.pdf pages 19 and 17
* https://github.com/taylorwirth4/ScrippsPierSCS_SASS/blob/main/correct_DO_with_sal.py
(Taylor is the instrument operator)

The corrections are only done to O2con, and the units are uM (also different
from the SBE63.

Also, unlike the SBE63, the coefficients do not appear to change, and so
can be hardcoded.

ELD
5/18/2022

"""

import math


def salinity_correction(salinity, temperature, salinity_property):
    """Calculate the Aanderaa Salinity correction.

    This calculation is almost identical to the SBE63 equation, but with
    different coefficients.  From the manual:

    calculated from the following equation:
    O2_corrected = O2 * exp [S * (B0 + B1 * Ts
                                     + B2 * Ts^2
                                     + B3 * Ts^3) + C0 * S2]

    where:
    O2 is the measured O2 concentration in µM
    S = measured salinity in ppt or PSU
    Ts = scaled temperature = ln [(298.15 – t) / (273.15 + t)]
    t = temperature, °C
    B0 = -6.24097e-3
    B1 = -6.93498e-3
    B2 = -6.90358e-3
    B3 = -4.29155e-3
    C0 = -3.11680e-7
    """
    # Coefficients from manual
    B0 = -0.00624097
    B1 = -0.00693498
    B2 = -0.00690358
    B3 = -0.00429155
    C0 = -0.00000031168

    tscale = math.log((298.15 - temperature) / (273.15 + temperature))

    SCorr = math.exp((salinity - salinity_property) *
                     (B0
                      + B1 * tscale
                      + B2 * tscale ** 2
                      + B3 * tscale ** 3) + C0 * salinity ** 2)
    return SCorr


def pressure_correction(pressure):
    """Calculate the Aanderaa Pressure correction.

    From manual:
    The response of the sensing foil decreases to some extent with the
    ambient water pressure (3.2% lower response per 1000 m of water depth or dbar
    – investigated in detail by Uchida et al., 2008, for full reference see
    publication list in appendix 11). This effect is the same for all AADI oxygen
    Optodes and is totally and instantly reversible and easy to compensate for.

    The depth compensated O2 concentration, O2c, is calculated from the following equation:
    O2c = O2 * (1 + (0.032 * d)/1000)
    where:
    d is depth in meters or pressure in dbar.
    O2 is the measured O2 concentration in either µM or %.
    The unit of the compensated O2 concentration, O2c, depends on the unit of the O2 input
    """
    Pcorr = 0.032

    return 1 + abs(pressure) / 1000 * Pcorr


def correct_oxygen(O2_uM, temperature, salinity=0, pressure=0,
                   salinity_property=0, **kwargs):
    """Apply Salinity and Pressure corrections to Oxygen.

    Inputs
        O2_uM (µM): Dissolved oxygen recorded by Aanderaa with no salinity compensation applied
        temperature (ºC): Temperature measured by Aanderaa or auxiliary thermometer
        pressure (dbar): Pressure measured by auxiliary pressure sensor
        salinity (PSU): Salinity measured by auxiliary salinity/conductivity sensor
        salinity_property (PSU): Salinity input into Aanderaa pre-deployment, usually 0
    """
    Scorr = salinity_correction(salinity, temperature, salinity_property)
    Pcorr = pressure_correction(pressure)

    oxygen = O2_uM * Scorr * Pcorr

    return oxygen
