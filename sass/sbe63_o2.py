#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Define the equations that calibrate O2.

Oxygen in the SASS system is measured using a Sea-Bird Scientific SBE 63
Optical Dissolved Oxygen Sensor. The output from  the instrument consists of
2 variables: units of phase (µsec) and temperature voltage (V). First instrument
temperature is calculated, and then that is used to calculate oxygen in units
of ml/l.

The temperature sensor is different from the CTD's, and it is calibrated separately.
The equations for the temperature calibration came from an example of the calibration
sheet provided by SBE. These values are entered in the SASS Inventory and Cleaning google
spreadsheet under the tab "SBE 63 O2".

The equations for the oxygen calculation come from the SBE63 manual (PDF included in
references). It is broken into pieces for the pressure correction, the salinity correction,
the Stern-Volmer constant, and the penultimate calculation.

ELD
8/26/2021

"""

import math


def calibrate_temperature(voltage, ta0, ta1, ta2, ta3, **kwargs):
    """Calibrate the temperature sensor of an SBE63 oxygen probe.

    Note: this is sensor temperature, not water temp or sea surface temp. It can
    be discarded after oxygen is calculated.

    From the calibration sheet:
    Temperature [ deg C] = 1 / (TA0 + TA1*L + TA2*L^2 + TA3*L^3) - 273.15S
    where:
    L = ln (100000 * thermistor_voltage / (3.3 - thermistor_voltage))

    """
    lscale = math.log(100000 * voltage / (3.3 - voltage))
    temperature = 1 / (ta0 + ta1 * lscale
                       + ta2 * lscale ** 2
                       + ta3 * lscale ** 3) - 273.15

    return temperature


def stern_volmer_constant(temperature, c0, c1, c2):
    """Calculate the Stern-Volmer constant.

    from SBE manual SBE_63_Dissolved_Oxygen_Sensor.pdf revision 011, page 47

    The Stern-Volmer constant equation is:
    Ksv = c0 + c1T + c2T**2
    where:
    * c0, c1, c2: calibration coefficients
    * T: temperature output from SBE 63’s thermistor in °C
    """
    Ksv = c0 + (c1 * temperature) + (c2 * temperature ** 2)

    return Ksv


def salinity_correction(salinity, temperature):
    """Calculate the SBE63 Salinity correction.

    from SBE manual SBE_63_Dissolved_Oxygen_Sensor.pdf revision 011, page 47
    The salinity correction equation is:
    SCorr = exp [S * (SolB0 + SolB1 * Ts
                      + SolB2 * Ts^2+ SolB3 * Ts^3) + SolC0 * S2]

    where Salinity correction coefficients are constants
    (Benson and Krause, 1984):
    SolB0 = -6.24523e-3
    SolB1 = -7.37614e-3
    SolB2 = -1.03410e-2
    SolB3 = -8.17083e-3
    SolC0 = -4.88682e-7 and
    Ts = ln [(298.15 – T) / (273.15 + T)]
    where
    T: temperature output from SBE 63’s thermistor in °C
    S: salinity (from associated CTD)
    """
    solb0 = -6.24523e-3
    solb1 = -7.37614e-3
    solb2 = -1.03410e-2
    solb3 = -8.17083e-3
    solc0 = -4.88682e-7
    tscale = math.log((298.15 - temperature) / (273.15 + temperature))

    SCorr = math.exp(salinity * (solb0
                                 + solb1 * tscale
                                 + solb2 * tscale ** 2
                                 + solb3 * tscale ** 3) + solc0 * salinity ** 2)
    return SCorr


def pressure_correction(pressure, temperature, E):
    """Calculate the SBE63 Salinity correction.

    from SBE manual SBE_63_Dissolved_Oxygen_Sensor.pdf revision 011, page 47
    The pressure correction equation is:
    Pcorr = exp (E * P / K)
    where
    Pressure correction coefficient is constant E = 0.011
    K: temperature in Kelvin = T + 273.15
    T: temperature output from SBE 63’s thermistor in °C
    P: pressure (dbar) (from associated CTD)
    """
    temperature_k = temperature + 273.15
    Pcorr = math.exp(E * pressure / temperature_k)

    return Pcorr


def calibrate_oxygen(output, temperature, salinity=0, pressure=0,
                     A0=None, A1=None, A2=None, B0=None, B1=None,
                     C0=None, C1=None, C2=None, E=None, **kwargs):
    """Calculate oxygen from calibration coefficients and output of the SBE63.

    From the manual:
    The SBE 63’s luminescence decay time decreases non-linearly with increasing
    oxygen concentration. Because the phase delay between excited and emitted
    signals is shifted as a function of the ambient oxygen concentration, the phase
    delay is detected instead of the decay time. The signal is characterized by a
    modified Stern-Volmer equation as follows:
    O2 (ml/L) = [((a0 + a1*T + a2*V^2) / (b0 + b1*V) – 1) / K_sv ] [S_Corr ] [P_Corr ]
    Where
    T: temperature output from SBE 63’s thermistor in °C
    V: raw measured phase delay in volts = output / 39.457071
    output: raw measured phase delay in microseconds
    and other  corrections are as shown above.
    """
    vscale = output / 39.457071
    atmp = A0 + A1 * temperature + A2 * vscale ** 2
    btmp = B0 + B1 * vscale

    Ksv = stern_volmer_constant(temperature, C0, C1, C2)
    Scorr = salinity_correction(salinity, temperature)
    Pcorr = pressure_correction(pressure, temperature, E)

    oxygen = ((atmp / btmp - 1) / Ksv) * Scorr * Pcorr

    return oxygen
