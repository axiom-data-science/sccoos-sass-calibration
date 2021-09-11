import pandas as pd
from pathlib import Path
from ..sbe63_o2 import calibrate_temperature, calibrate_oxygen
from ..utilities import proper_rounding


here = Path(__file__).parent


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

    # call the calibration on each row of the dataframe separately
    cali_check['temp_calc'] = cali_all.apply(lambda x:
                                             calibrate_temperature(*x[['Instrument_Output_[V]',
                                                                       'TA0', 'TA1', 'TA2', 'TA3']]), axis=1)
    # check the calculation
    data = pd.DataFrame({})
    data['test1'] = cali_check['Instrument_Temperature_[C]'].map(lambda x: proper_rounding(x, 5))
    data['test2'] = cali_check['temp_calc'].map(lambda x: proper_rounding(x, 5))
    pd.testing.assert_series_equal(data['test1'], data['test2'], check_names=False)


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

    # call the calibration on each row of the dataframe separately
    cali_check['oxygen_calc'] = cali_all.apply(lambda x: calibrate_oxygen(**x), axis=1)

    # This does not give the exact same answer for a few reasons:
    #  - The values on the PDF sheet are all rounded to 3 decimal places
    #  - Instrument temperature is not given on the sheet, so this uses nominal bath temperature
    #  - Do not know if there should be a pressure correction in the calibration lab (salinity=0)
    cali_check['diff'] = cali_check['Instrument_Oxygen_[ml/l]'] - cali_check['oxygen_calc']
    assert cali_check['diff'].abs().max() < .006
    data = pd.DataFrame({})
    data['test1'] = cali_check['Instrument_Oxygen_[ml/l]'].map(lambda x: proper_rounding(x, 1))
    data['test2'] = cali_check['oxygen_calc'].map(lambda x: proper_rounding(x, 1))
    pd.testing.assert_series_equal(data['test1'], data['test2'], check_names=False)
