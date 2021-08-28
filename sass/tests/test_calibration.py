import pandas as pd
from pathlib import Path
from sass.chlorophyll import calibrate_chlorophyll
from sass.sbe63 import calibrate_temperature, calibrate_oxygen

here = Path(__file__).parent


def test_chlorophyll():
    """ test chlorophyll calibration using file prepared by Mel that includes the calibration coefficients in it.

    :return:
    """
    # Mel did the calculations by hand in an Excel spreadsheet. Liz transferred those to a Google Sheet, and then
    # downloaded a tidy version as a CSV file.
    filename = here.joinpath('resources/chlorophyll/SIOpier_examplesCHL_20210817.csv')
    data = pd.read_csv(filename)
    data.rename(columns={'Volt2': 'output',
                         'SF': 'scale_factor',
                         'CWO': 'clean_water_offset'}, inplace=True)

    data['calculated_chlor'] = calibrate_chlorophyll(**data)
    assert data['calculated_chlor'].round(8).equals(data['chl_[ug/l]'].round(8))


def test_sbe63_temperature():
    """ SBE63 has its own temperature sensor that outputs voltage """

    # For testing, Liz downloaded the tab "SBE 63 O2" from the SASS Inventory and Cleaning Google Sheet.
    # Removing the empty columns is needed when reading from the Sheet
    filename = here.joinpath('resources/oxygen/calibration_coefficients_20210826.csv')
    coefficients = pd.read_csv(filename)
    coefficients['date'] = pd.to_datetime(coefficients['START TIME'])
    # remove nonsense columns
    unnamed = [name for name in coefficients.columns if "Unnamed" in name]
    coefficients.drop(columns=unnamed, inplace=True)
    assert coefficients.shape == (4, 17)

    # To create values to check against, values were hand copied from the PDF of the calibration sheet for
    # instrument 1069. The column names are taken from the calibration sheet. The number of decimal places is
    # limited to 3 because that is what was printed on the sheet.
    temperature_file = here.joinpath('resources/oxygen/Temperature_calibrations_1069.csv')
    cali_check = pd.read_csv(temperature_file)
    # Add a date that corresponds to when this instrument was used in the calibration coefficient file
    cali_check['date'] = pd.to_datetime("2021-07-01T00:00:00", format='%Y-%m-%dT%H:%M:%S')

    # Merge the coefficients and "data" together so that the correct coefficients are used at the right times
    cali_all = pd.merge_asof(cali_check, coefficients, on=['date'], direction='backward')

    cali_check['calc_temp'] = cali_all.apply(lambda x:
                                             calibrate_temperature(*x[['Instrument_Output_[V]',
                                                                       'TA0', 'TA1', 'TA2', 'TA3']]), axis=1)
    assert cali_check['Instrument_Temperature_[C]'].round(3).equals(cali_check['calc_temp'].round(3))


def test_sbe63_oxygen():
    """ SBE63 has an oxygen sensor that outputs phase or something """

    # For testing, Liz downloaded the tab "SBE 63 O2" from the SASS Inventory and Cleaning Google Sheet.
    # Removing the empty columns is needed when reading from the Sheet
    filename = here.joinpath('resources/oxygen/calibration_coefficients_20210826.csv')
    coefficients = pd.read_csv(filename)
    coefficients['date'] = pd.to_datetime(coefficients['START TIME'])
    # remove nonsense columns
    unnamed = [name for name in coefficients.columns if "Unnamed" in name]
    coefficients.drop(columns=unnamed, inplace=True)
    assert coefficients.shape == (4, 17)

    # To create values to check against, values were hand copied from the PDF of the calibration sheet for
    # instrument 1069. The column names are taken from the calibration sheet. The number of decimal places is
    # limited to 3 because that is what was printed on the sheet.
    oxygen_file = here.joinpath('resources/oxygen/Oxygen_calibrations_1069.csv')
    cali_check = pd.read_csv(oxygen_file)
    # Add a date that corresponds to when this instrument was used in the calibration coefficient file
    cali_check['date'] = pd.to_datetime("2021-07-01T00:00:00", format='%Y-%m-%dT%H:%M:%S')

    # Merge the coefficients and "data" together so that the correct coefficients are used at the right times
    cali_all = pd.merge_asof(cali_check, coefficients, on=['date'], direction='backward')
    cali_all.rename(columns={'Bath_Temp_[C]': 'temperature',
                             'Bath_Salinity_[psu]': 'salinity',
                             'Instrument_Output_[usec]': 'output'}, inplace=True)
    cali_all['pressure'] = 0

    cali_check['oxygen'] = cali_all.apply(lambda x: calibrate_oxygen(**x), axis=1)

    # This does not give the exact same answer for a few reasons:
    #  - The values on the PDF sheet are all rounded to 3 decimal places
    #  - Instrument temperature is not given on the sheet, so this uses nominal bath temperature
    #  - Do not know if there should be a pressure correction in the calibration lab (salinity=0)
    cali_check['diff'] = cali_check['Instrument_Oxygen_[ml/l]'] - cali_check['oxygen']
    assert cali_check['diff'].abs().max() < .006
    assert cali_check['Instrument_Oxygen_[ml/l]'].round(1).equals(cali_check['oxygen'].round(1))
