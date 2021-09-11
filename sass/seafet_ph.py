"""

    pH in the SASS system is measured with a SBE SeaFET instrument. There are two sensors on the SeaFET -
    an internal sensor enclosed in gel, that is more accurate in general, and an external sensor that
    can be more accurate with corrected for salinity. Voltages and initial values are included for
    both these in the raw data files. The external pH was produced using an average salinity for the
    area.

    The possibility of re-computing internal pH is included it for testing purposes. The meat of the routine
    is correcting the external pH.

    From the technical note, Technical_Note_Calculating_pH_AppNote.pdf (Application Note 99 from SBE):
    "This application note provides formulas to calculate pHTotal from raw ISFET
    voltage (VFET/REF ) and CTD data. Formulas for calculating pH Internal and pH External
    from a Shallow SeaFET/SeapHOx V ... are listed below. "
    More details can be found in:

    T. R. Martz, J. G. Connery, K. S. Johnson. Testing the Honeywell Durafet for seawater
    pH applications. Limnol. Oceanogr.: Methods, 8:172-184, 2010.

    K. S. Johnson, H. W. Jannasch, L. J. Coletti, V. A. Elrod, T. R. Martz,Y. Takeshita,
    R. J. Carlson, and J. G. Connery. Deep-Sea DuraFET: A pressure tolerant pH sensor designed
    for global sensor networks. Analytical Chemistry, 88:3249-3256, 2016.
"""

import math


def calibrate_ph(voltage, temperature, salinity=0, external=False, k0=None, k2=None, **kwargs):
    """ A function that can calibrate either internal (for checking) or external pH
    This comes from the technical note.
    The internal electrolyte gel electrochemical cell exhibits a Nernstian response to
    pH and has a negligible response to the chloride activity (Martz et al. 2010).

    The solid state electrochemical cell exhibits a Nernstian response to pH with additional
    corrections due to it being sensitive to the chloride activity of salt water (Johnson
    et al. 2016).

    """
    # Constants
    R = 8.3144621  # J/(K mol)  Universal gas constant
    F = 96485.365  # C/mol  Faraday Constant

    # unit conversions
    temperature_k = temperature + 273.15  # Temperature in Kelvin

    # Nernstian correction
    s_nernst = (R * temperature_k * math.log(10)) / F

    ph = (voltage - k0 - k2 * temperature) / s_nernst
    if external:
        # add the corrections
        pass

    return ph
