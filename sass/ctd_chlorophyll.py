"""

    Chlorophyll is calculated using the Volt 2 output from each SASS CTD. Calibration coefficients
    consist of the clean water offset (CWO) and scale factor (SF), which are determined during calibration
    of the instrument by Seabird (SBE).

    Upon receipt of a newly  calibrated instrument from seabird, the CWO and SF sheets are stored as a
    hardcopy in a binder titled SASS FLUOROMETERS and as a PDF in the SASS shared Google Drive.
    When a new fluorometer is deployed, the CWO and SF for that fluorometer is entered into the
    SASS Inventory and Cleaning google spreadsheet, along with the exact deployment time.

    An example calibration sheet is included in the references folder of this project.

    ELD (Axiom)
    8/26/2021

"""


def calibrate_chlorophyll(output, scale_factor=None, clean_water_offset=None, **kwargs):
    """ Calculate chlorophyll from input voltage.

    The equation specified on a calibration sheet is:

    CHL(ug/l) = Scale Factor x (Output - Clean Water Offset)
    where:
    Clean Water Offset (CWO): signal output of the fluorometer in pure filtered de-ionized water (Volts)
    Scale Factor (SF): multiplier determined at WET Labs using a liquid fluorescent standard
    and a reference fluorometer whose chlorophyll fluorescence response has been characterized
    using a mono-species culture. (ug/l/V)
    Output: signal output of the fluorometer (Volts)
    """

    return (output - clean_water_offset) * scale_factor
