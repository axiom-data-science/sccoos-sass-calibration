# Architecture

This project was designed with these assumptions

* Multiple sites have to be supported and the sites where instruments are installed may change over the years.
* Instruments installed at sites may also change.
* Different calibrations coefficients will apply during different instrument deployments.
* Calibration coefficients are currently stored in a Google Sheet, but that might changes as the system matures.
* SCCOOS personnel should partly be responsible for maintaining the instrument configurations because they are 
installing them at the sites.
* The end goal is for this system to be running automatically in real-time.

Table of Contents:

[[_TOC_]]

## Classes

The following classes are required for this system to function.

### Station

Currently, there are 4 SASS stations. These are physical locations where instruments are installed. These will be 
tracked using a JSON file that is stored in git and can be updated by SCCOOS personnel as new stations are installed 
or decommissioned.

Attributes of stations include:
* id/code ("sio", etc.)
* label ("Scripps Pier")
* latitude
* longitude
* installation date
* decommission date
* maintainer
* maintainer (email or phone number)
* notes
* attributions/agents/funders
* InstrumentSets [list of set ids] - see below

These attributes are defined so that this JSON could be used as the input to a source manager if that is needed.

### InstrumentSet

The InstrumentSet defines what collection of instruments is installed at a site.  This is important for several reasons:
1. It determines which calibrations should be performed for each station. 
2. The format of each station's raw data depends on the InstrumentSet. However, those files don't have column headers,
so they need to be tracked.
3. The calibration coefficients are stored in a tab on a Google Sheet. There is no rhyme or reason to the tab names,
so those need to be tracked also.

There is the possibility that instruments might be added or removed from a site, so these sets might change in time.  
However, installation of a specific individual instrument (i.e. instrument 1059 vs 1044) is not relevant.

InstrumentType attributes include:
* id (sio1)
* station code/id (location)
* start date
* end date
* raw data url
* columns headers to be used in pd.read_csv(url) [temperature, pressure, salinity, ... ]
* calibration location
  * Google Sheet url (in case that changes)
  * tab names {"oxygen": "SIO O2"}
  
### Calibration

Calibration coefficients change everytime an instrument is replaced. They are tracked for now in a Google Sheet 
administered by SCCOOS. However, that might change in the future. Therefore, I want to start developing a schema that
could be used in a future database.  Attributes:

* deployment start date
* deployment end date
* coefficients {"T0": .1120, "T1": 1e-3} - these will be different depending on columns in the Google Sheet
* instrument (sbe63)
* parameter (oxygen)
* calibration date (if available)
* modification date (when added to the spreadsheet)

## Usage of Classes

How to calibrate a station that's only had one set-up:

1. Read station.json to identify the InstrumentSet (Initially there is only 1 set-up per station)
2. Using the URL in the InstrumentSet, read the raw data
3. For each parameter to calibrate\
  a. read the calibration coefficients from the tab on the Sheet\
  b. merge the data with the calibrations\
  c. call the calibration routine\
  d. append the calibrated data to the raw data
4. Write the new data file [where = TBD]



