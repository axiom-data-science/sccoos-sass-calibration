# Architecture

This project was designed with these assumptions

* Multiple sites have to be supported and the sites where instruments are installed may change over the years.
* Instruments installed at sites may also change.
* Different calibrations coefficients will apply during different instrument deployments.
* Calibration coefficients are currently stored in a Google Sheet, but that might changes as the system matures.
* SCCOOS personnel should partly be responsible for maintaining the instrument configurations because they are 
installing them at the sites.
* The end goal is for this system to be running automatically in real-time.
* Calibrations will also have to be done for times past to correct errors.

Table of Contents:

[[_TOC_]]

## Classes

The following classes are required for this system to function.

### InstrumentSet

The InstrumentSet defines what collection of instruments is installed at a site.  This is important for several reasons:
1. It determines which calibrations should be performed for each station. 
2. The format of each station's raw data depends on the InstrumentSet. 
  However, those files don't have column headers, so they need to be tracked.
3. The calibration coefficients are stored in a tab on a Google Sheet. There 
is no rhyme or reason to the tab names, so those need to be tracked also.

The type of instruments installed at a site might change so a station will 
have multiple instrument sets in time. However, the installation of a 
specific individual instrument (i.e. instrument 1059 vs 1044) does not seem 
to be relevant beyond identifying the correct calibrations to use in 
processing.

InstrumentType attributes include:
* id (sio1)
* station code/id (location)
* start date
* end date
* raw data url
* columns headers to be used in pd.read_csv(url) [temperature, pressure, salinity, ... ]
* calibration location
  * Google Sheet url (in case that changes)
  * ~~tab names {"oxygen": "SIO O2"}~~ = It's nice to track human readable 
  names, but the code does not use them.
  * tab gids - the identifiers that Google uses in the URLs


## Usage of Instrument Set

How to calibrate a station that's only had one set-up:

1. Instrument set (and dates) are specified in the call of sass
2. Using the URL in the InstrumentSet, read the raw data
3. For each parameter to calibrate\
  a. read the calibration coefficients from the tab on the Sheet\
  b. merge the data with the calibrations\
  c. call the calibration routine\
  d. append the calibrated data to the raw data
4. Write the new data file


## Other Concepts (maybe classes in the future but not now)

### Station

Currently, there are 4 SASS stations. These are physical locations where 
instruments are installed. I worked up an initial version of these intending
that the list would be updated by SCCOOS personnel as stations are installed 
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

However, I later realised that the instrument sets at a station are 
essentially independent of each other. Additionally, all the station 
information will be in packrat, and there are so few of them that they will 
not need a station manager. 

I moved the initial iteration of this in the references directory in case we 
go back to it in the future.

  
### Calibration

Calibration coefficients change every time an instrument is replaced. They 
are tracked for now in a Google Sheet administered by SCCOOS. However, that 
might change in the future. Therefore, we might need a schema for them 
for a future database.  Attributes:

* deployment start date
* deployment end date
* coefficients {"T0": .1120, "T1": 1e-3} - these will be different depending on columns in the Google Sheet
* instrument model (i.e. SBE63)
* instrument serial number (for individual instrument deployed)
* parameter (oxygen)
* calibration date (if available)
* modification date (when added to the spreadsheet)



