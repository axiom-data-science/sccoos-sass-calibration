import math


def calibrate_temperature(voltage, ta0, ta1, ta2, ta3, **kwargs):
    L = math.log(100000 * voltage / (3.3 - voltage))
    temperature = 1 / (ta0 + (ta1 * L) + (ta2 * L ** 2) + (ta3 * L ** 3)) - 273.15

    return temperature


def stern_volmer_constant(T, c0, c1, c2):
    """ Calculate the Stern-Volmer constant
    from SBE manual SBE_63_Dissolved_Oxygen_Sensor.pdf revision 011, page 47
    The Stern-Volmer constant equation is: Ksv = c0 + c1T + c2T**2

    where
    * c0, c1, c2 are calibration coefficients
    * T is temperature output from SBE 63’s thermistor in °C
    """

    Ksv = c0 + (c1 * T) + (c2 * T ** 2)
    return Ksv


def salinity_correction(S, T):
    """ Calculate the SBE63 Salinity correction
    from SBE manual SBE_63_Dissolved_Oxygen_Sensor.pdf revision 011, page 47
    The salinity correction equation is:
    SCorr = exp [S * (SolB0 + SolB1 * Ts + SolB2 * Ts^2+ SolB3 * Ts^3) + SolC0 * S2]

    where
    * Salinity correction coefficients are constants (Benson and Krause, 1984) -
    SolB0 = -6.24523e-3
    SolB1 = -7.37614e-3
    SolB2 = -1.03410e-2
    SolB3 = -8.17083e-3
    SolC0 = -4.88682e-7
    * Ts = ln [(298.15 – T) / (273.15 + T)]
    where T is temperature output from SBE 63’s thermistor in °C
    * S = salinity (from associated CTD)
    """
    SolB0 = -6.24523e-3
    SolB1 = -7.37614e-3
    SolB2 = -1.03410e-2
    SolB3 = -8.17083e-3
    SolC0 = -4.88682e-7
    Ts = math.log((298.15 - T) / (273.15 + T))

    SCorr = math.exp(S * (SolB0 + SolB1 * Ts + SolB2 * Ts ** 2 + SolB3 * Ts ** 3) + SolC0 * S ** 2)

    return SCorr


def pressure_correction(P, T, E):
    """ Calculate the SBE63 Salinity correction
    from SBE manual SBE_63_Dissolved_Oxygen_Sensor.pdf revision 011, page 47
    The pressure correction equation is:
    Pcorr = exp (E * P / K)
    where
    * Pressure correction coefficient is constant E = 0.011
    * K = temperature in Kelvin = T + 273.15
    where T is temperature output from SBE 63’s thermistor in °C
    * P = pressure (dbar) from CTD data
    """
    K = T + 273.15
    Pcorr = math.exp(E * P / K)

    return Pcorr


def calibrate_oxygen(output, temperature, salinity=0, pressure=0,
                     A0=None, A1=None, A2=None, B0=None, B1=None,
                     C0=None, C1=None, C2=None, E=None, **kwargs):
    v = output / 39.457071
    t = temperature
    k = t + 273.15  # temperature in Kelvin
    s = salinity

    atmp = A0 + A1 * t + A2 * v ** 2
    btmp = B0 + B1 * v
    Ksv = stern_volmer_constant(temperature, C0, C1, C2)
    Scorr = salinity_correction(salinity, temperature)
    Pcorr = pressure_correction(pressure, temperature, E)
    oxygen = ((atmp / btmp - 1) / Ksv) * Scorr * Pcorr

    return oxygen
