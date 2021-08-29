# sccoos-sass-calibration

sccoos-sass-calibration is a tool written in Python that will to convert raw voltages from SCCOOS's automated shore 
stations into oxygen, pH, and chlorophyll.

The raw data are posted online by Scripps. The equations for the calibrations are provided by the manufacturers of the
sensors. The calibration coefficients are posted by SCCOOS in a Google Sheet. After calibration, the data will be
posted [at a location hosted by Axiom TBD] for ingestion into the Axiom's sensor system and posting on ERDDAP.

## Prerequisites

Before you begin, ensure you have met the following requirements:

* Conda environment [TBD]
<!--- These are just example requirements. Add, duplicate or remove as required
* You have installed the latest version of `<coding_language/dependency/requirement_1>`
* You have a `<Windows/Linux/Mac>` machine. State which OS is supported/which is not.
* You have read `<guide/link/documentation_related_to_project>`.
--->

## Installing <project_name>

To install <project_name>, follow these steps:

Linux and macOS:
```
<install_command>
```

Windows:
```
<install_command>
```
## Using <project_name>

To use SASS, follow these steps:

```
python ./run_sass.py --start "2021-08-01T00:00:00" --end "2021-08-02T00:00:00" --station "sio"
```
Arguments include:
* start date (required)
* end date (required)
* station code (optional - does all if not specified)

<!--- 
## Contributing to <project_name>
If your README is long or you have some specific process or steps you want contributors to follow, 
consider creating a separate CONTRIBUTING.md file
To contribute to <project_name>, follow these steps:

1. Fork this repository.
2. Create a branch: `git checkout -b <branch_name>`.
3. Make your changes and commit them: `git commit -m '<commit_message>'`
4. Push to the original branch: `git push origin <project_name>/<location>`
5. Create the pull request.

Alternatively see the GitHub documentation on [creating a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).
--->

## Contributors

Thanks to the following people who have contributed to this project:

* [@liz](https://github.com/eldobbins) 📖
<!---* [@cainwatson](https://github.com/cainwatson) 🐛
* [@calchuchesta](https://github.com/calchuchesta) 🐛 

You might want to consider using something like the [All Contributors](https://github.com/all-contributors/all-contributors) specification and its [emoji key](https://allcontributors.org/docs/en/emoji-key).
--->
## Contact

If you want to contact me you can reach me at <liz@axiomdatascience.com>.

## License
<!--- If you're not sure which open license to use see https://choosealicense.com/--->

This project uses the following license: <!--- [<license_name>](<link>). ---> [TBD]