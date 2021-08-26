import pandas as pd
from sass.chlorophyll import calibrate_chlorophyll


def test_chlorophyll():
    """ test chlorophyll calibration using file prepared by Mel that includes the calibration coefficients in it.

    :return:
    """
    # Mel did the calculations by hand in an Excel spreadsheet. Liz transferred those to a Google Sheet, and then
    # downloaded a tidy version as a CSV file.
    filename = 'resources/chlorophyll/SIOpier_examplesCHL_20210817.csv'
    data = pd.read_csv(filename)

    data['chlor'] = calibrate_chlorophyll(data['Volt2'],
                                          data['SF'],
                                          data['CWO'])
    assert data['chlor'].round(8).equals(data['chl_[ug/l]'].round(8))