"""

    pH in the SASS system is measured with a SBE SeaFET instrument.
    There are 2 sensors on a SeaFET - an internal sensor enclosed in gel, that is more
    accurate in general, and an external sensor that can be more accurate when corrected
    with salinity. Voltages and initial values are included for both these in the raw
    data files. The external pH was produced using an average salinity for the
    area.

    The possibility of re-computing internal pH is included it for testing purposes.
    The meat of the routine is correcting the external pH.

    From the technical note, Technical_Note_Calculating_pH_AppNote.pdf
    (Application Note 99 from SBE):
    "This application note provides formulas to calculate pHTotal from raw ISFET
    voltage (VFET/REF ) and CTD data. Formulas for calculating pH Internal and pH External
    from a Shallow SeaFET/SeapHOx V ... are listed below. "
    More details can be found in:

    T. R. Martz, J. G. Connery, K. S. Johnson. Testing the Honeywell Durafet for seawater
    pH applications. Limnol. Oceanogr.: Methods, 8:172-184, 2010.

    K. S. Johnson, H. W. Jannasch, L. J. Coletti, V. A. Elrod, T. R. Martz,Y. Takeshita,
    R. J. Carlson, and J. G. Connery. Deep-Sea DuraFET: A pressure tolerant pH sensor
    designed for global sensor networks. Analytical Chemistry, 88:3249-3256, 2016.
"""

import math


def total_chloride_in_seawater(salinity):
    """Calculate the Total chloride in seawater
    as in:
    A. G. Dickson, C. L. Sabine, and J. R. Christian. IOCCP Report No. 8, 2007.

    salinity is in psu
    """
    Cl_total = (0.99889 / 35.453) * (salinity / 1.80655) \
        * (1000 / (1000 - 1.005 * salinity))

    return Cl_total


def sample_ionic_strength(salinity):
    """Calculate the Sample Ionic Strength
    as in:
    A. G. Dickson, C. L. Sabine, and J. R. Christian. IOCCP Report No. 8, 2007.

    salinity is in psu
    """
    return (19.924 * salinity) / (1000 - 1.005 * salinity)


def dubye_huckel_hci(temperature):
    """ Calculate the Debye-Huckel constant for activity of HCl
    as in:
    K. H. Khoo, R. W. Ramette, C. H. Culberson, and R. G. Bates. Determination of hydrogen
    ion concentrations in seawater from 5C to 40C: standard potentials at salinities 20 to 45%.
    Analytical Chemistry, 49:29-24, 1977.

    temperature is in degrees Celsius
    """
    A_DH = 0.0000034286 * temperature ** 2 \
        + 0.00067524 * temperature \
        + 0.49172143
    return A_DH


def log_of_HCl_activity_coefficient(A_DH, ionic_strength, temperature):
    """ Calculate the Logarithm of HCl activity coefficient as a function of temperature
    as in:
    K. H. Khoo, R. W. Ramette, C. H. Culberson, and R. G. Bates. Determination of hydrogen
    ion concentrations in seawater from 5C to 40C: standard potentials at salinities 20 to 45%.
    Analytical Chemistry, 49:29-24, 1977.

    A_DH is the Debye-Huckel constant for activity of HCl
    ionic-strength is the ionic strength
    temperature is in degrees Celsius
    """
    log_chi_HCl  = (-A_DH * math.sqrt(ionic_strength)) / (1 + 1.394 * math.sqrt(ionic_strength)) \
        + (0.08885 - 0.000111 * temperature) * ionic_strength

    return log_chi_HCl


def total_sulfate_in_seawater(salinity):
    """Calculate the Total sulfate in seawater
    as in:
    A. G. Dickson, C. L. Sabine, and J. R. Christian. IOCCP Report No. 8, 2007.

    salinity is in psu
    """
    S_total = (0.1400 / 96.062) * (salinity / 1.80655)

    return S_total


def acid_dissociation_HSO4(salinity, temperature, ionic_strength):
    """Calculate the Acid dissociation constant of HSO 4  ̄
    as in:
    A. G. Dickson, C. L. Sabine, and J. R. Christian. IOCCP Report No. 8, 2007.

    salinity is in psu
    temperature is in degrees Celsius (will be converted to Kelvin)
    ionic_strength is ionic strength
    """
    # unit conversions
    temperature_k = temperature + 273.15  # Temperature in Kelvin

    ln_T = math.log(temperature_k)

    # for that crazy exponent
    term1 = -4276.1 / temperature_k
    term2 = 141.328
    term3 = -23.093 * ln_T
    term4 = ((-13856 / temperature_k) + 324.57 - 47.986 * ln_T) * math.sqrt(ionic_strength)
    term5 = ((35474 / temperature_k) - 771.54 + 114.723 * ln_T) * ionic_strength
    term6 = -1 * (2698 / temperature_k) * ionic_strength ** 1.5
    term7 = (1776 / temperature_k) * ionic_strength ** 2

    Ks = (1 - 0.001005 * salinity) \
        * math.exp(term1 + term2 + term3 + term4 + term5 + term6 + term7)

    return Ks


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
        # define the corrections
        Cl_total = total_chloride_in_seawater(salinity)
        ionic_strength = sample_ionic_strength(salinity)
        A_DH = dubye_huckel_hci(temperature)
        S_total = total_sulfate_in_seawater(salinity)
        Ks = acid_dissociation_HSO4(salinity, temperature, ionic_strength)
        log_chi_HCl = log_of_HCl_activity_coefficient(A_DH, ionic_strength, temperature)

        # add the corrections
        ph = ph \
            + math.log10(Cl_total) \
            + 2 * log_chi_HCl \
            - math.log10(1 + S_total / Ks) \
            - math.log10((1000 - 1.005 * salinity) / 1000 )

    return ph
