import pandas as pd
from pathlib import Path
from ..ctd_chlorophyll import calibrate_chlorophyll
from ..utilities import proper_rounding


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

    # calculate chlorophyll from output and calibration coefficients
    data['chlor_calc'] = calibrate_chlorophyll(**data)

    # check the result (shortage of decimal places in raw data causing some issues)
    data['test1'] = data['chl_[ug/l]'].map(lambda x: proper_rounding(x, 8))
    data['test2'] = data['chlor_calc'].map(lambda x: proper_rounding(x, 8))
    pd.testing.assert_series_equal(data['test1'], data['test2'], check_names=False)
