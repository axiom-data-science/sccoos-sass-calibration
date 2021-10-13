![Pipeline](http://git.axiom/axiom/sccoos-sass-calibration/badges/master/pipeline.svg)

# sccoos-sass-calibration

Applies calibration coefficients to the output of SCCOOS automated shore side instruments and writes out new files.

sccoos-sass-calibration is a tool written in Python that will to convert raw voltages from SCCOOS's automated shore 
stations into oxygen, pH, and chlorophyll.

The raw data are posted online by Scripps. The equations for the calibrations are provided by the manufacturers of the
sensors. The calibration coefficients are posted by SCCOOS in a Google Sheet. After calibration, the data will be
posted [at a location hosted by Axiom TBD] for ingestion into the Axiom's sensor system and posting on ERDDAP.

## Installing SASS

Installation
------------

This project relies on conda for installation and managing of the project dependencies.

1. [Download and install miniconda for your operating system](https://docs.conda.io/en/latest/miniconda.html).

2. Clone this project with `git`.

3.  Once conda is available build the environment for this project with:

    ```sh
    conda env create -f environment.yml
    ```

    The above command creates a new conda environment titled `sass_env` with the necessary project
    dependencies.

4. An Additional environment file is present for testing and development environments. The additional developer dependencies can be installed with
:

   ```sh
   conda env update -f test-environment.yml
   ```

## Using SASS

To use SASS, follow these steps:
1. Configure the instrument set in `sass/config/instrument_set.json`
2. Put the data to process in `sass/data/incoming`.  Note this can be a link to another directory. 
Also `data/outgoing` should exist
3.

```
./run_sass.py --start 2021-08-01 --end 2021-08-02 --set "np-ctd-2021"
```
Arguments include:
* start date (optional. If omitted, do the most recent 5 days)
* end date (optional.  If omitted, do a single day determined by start)
* set code (required.  Must match an entry in `instrument_set.json`)

Running Tests
-------------

To run the project's tests:

```
pytest -sv --integration
```

Building with Docker
--------------------

To build the docker container:

```
DOCKER_BUILDKIT=1 docker build -t sccoos-sass-calibration .
```

or have docker [BuildKit enabled by default](https://docs.docker.com/develop/develop-images/build_enhancements/).
To do that, set docker's daemon configuration in /etc/docker/daemon.json feature to true and restart the daemon:
> { "features": { "buildkit": true } }


Running with Docker
-------------------

```
docker run --rm --mount type=bind,source=/mnt/store/data/sensors/import/sccoos/sass,destination=/opt/sccoos-sass-calibration/data registry.axiom/sccoos-sass-calibration:latest ./call_sass.py --set np-ctd-2021
```

## Contributors

Thanks to the following people who have contributed to this project:

* [@liz](https://github.com/eldobbins) 📖
<!---* [@cainwatson](https://github.com/cainwatson) 🐛
* [@calchuchesta](https://github.com/calchuchesta) 🐛 

You might want to consider using something like the [All Contributors](https://github.com/all-contributors/all-contributors) specification and its [emoji key](https://allcontributors.org/docs/en/emoji-key).
--->
## Contact

If you want to contact me you can reach me at <liz@axiomdatascience.com>.

