
def calibrate_chlorophyll(voltage, sf, cwo):
    return (voltage - cwo) * sf
