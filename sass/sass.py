from pathlib import Path
import json
from . import instrument_set

here = Path(__file__).parent
stations_filename = 'config/stations.json'
instrument_set_filename = 'config/instrument_sets.json'


def load_configs(path_to_file):
    """

    :param path_to_file: Posix path to JSON configuration file
    :return:
    """
    with open(str(path_to_file), "r") as f:
        config_dict = json.loads(f.read())
    configs = []
    for config in config_dict['sets']:
        configs.append(instrument_set.InstrumentSet(**config))

    return configs


class SassCalibrationRunner:

    def run(self, start=None, end=None, station_id=None):

        print(f"{start} to {end} for station {station_id}")

        path = here.joinpath(instrument_set_filename)
        instrument_sets = load_configs(path)
        print(instrument_sets)
