import pandas as pd
from pathlib import Path
from ..seafet_ph import calibrate_ph
from ..utilities import proper_rounding

here = Path(__file__).parent


def test_ph_raw_data():
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


def test_ph_tech_note():
    """ Can function reproduce the values in the Technical Note
    Technical_Note_Calculating_pH_AppNote.pdf (Application Note 99 from SBE)
    """

    # from technical document
    v_int = -1.010404  # V
    v_ext = -.965858   # V
    k0_int = -1.438788
    k2_int = -1.304895e-3
    k0_ext = -1.429278
    k2_ext = -1.142026e-3
    temperature = 15.8735  # C
    salinity = 36.817      # psu

    ph = calibrate_ph(voltage=v_int, temperature=temperature,
                      external=False, k0=k0_int, k2=k2_int)
    print('\ninternal pH is', round(ph, 4))
    assert round(ph, 4) == 7.8310

    ph = calibrate_ph(voltage=v_ext, temperature=temperature, salinity=salinity,
                      external=True, k0=k0_ext, k2=k2_ext)
    print('external pH is', round(ph, 4))
    assert round(ph, 4) == 7.8454

    # should be
    # ph_int = 7.8310
    # ph_ext = 7.8454
