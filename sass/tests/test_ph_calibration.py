import pandas as pd
from pathlib import Path
from ..seafet_ph import calibrate_ph
from ..utilities import proper_rounding

here = Path(__file__).parent


def test_ph_internal():
    """ test to see if can match the internal pH that is included in the raw data file

    No fancy handling of calibration coefficients for this one.
    """
    # pH is complicated. Just copy coefficients from calibration sheet
    k0_int = -1.343051e0
    k2_int = -1.194458e-3

    # Read the raw data file. It doesn't have header. These work
    filename = here.joinpath('resources/pH/data-20210909_trimmed.dat')
    names = ['transmit_time',
             'ip',
             'serial_number',
             'measurement_time',
             'record',
             'flags',
             'ph_ext',
             'ph_int',
             'v_ext',
             'v_int',
             'temperature',
             'rh',
             'temperature_int']
    df = pd.read_csv(filename, names=names)
    df['time'] = pd.to_datetime(df['measurement_time'])

    # prep the input DataFrame and then calculate internal pH
    # Note: I also tried internal temperature and it didn't do as well as
    # the temperature with more decimal places
    data = df[['time', 'ph_int', 'v_int', 'temperature']].copy()
    data.rename(columns={'v_int': 'voltage'}, inplace=True)
    data['k0'] = k0_int
    data['k2'] = k2_int
    data['ph_int_calc'] = calibrate_ph(external=False, **data)

    # check the result (shortage of decimal places in raw data causing some issues)
    data['test2'] = data['ph_int_calc'].map(lambda x: proper_rounding(x, 4))
    data['test1'] = data['ph_int'].map(lambda x: proper_rounding(x, 3))
    data['test2'] = data['test2'].map(lambda x: proper_rounding(x, 3))
    pd.testing.assert_series_equal(data['test1'], data['test2'], check_names=False)
