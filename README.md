# Web scraping Grants on the Web panels

This package was written to scrape data on panel decisions from [Grants on the Web](https://gow.epsrc.ukri.org/) (GotW).

GotW is a web portal for accessing data on grants funded by the UK's [Engineering and Physical Sciences Research Council](https://www.ukri.org/councils/epsrc/) (EPSRC). The panel decision pages are of particular interest as they hold summary details of the outcomes, enabling the calculation of success rates. This allows one to see the number and value of grants successful, unsuccessful or treated in some other way (eg, passed to another panel).

The package automatically generates a list of all panels by interacting with the website via `selenium`. From this list one can then go to specific panel pages and scrape the data from them, returning a `pandas` dataframe containing all pertinent details.

## Important note about operating systems

This package relies on a Microsoft Edge driver to scrape the data, so you need to be on Windows with Edge isntalled for it to work.
