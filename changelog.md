# Changelog

## 0.1.0

- Better handling of multiple table types.
- Added panel id to output df for `retrieve_panel_decisions`.
- Enabled customised start date for searching in `get_panel_urls`.
- Included updated notebook which covers above changes.

## 0.0.11

- Remembered to port changes from notebook this time.

## 0.0.10

- Changed method for filtering rows in `tidy_tables` function (switched to .loc).
- Changed method for grabbing tables from URL to account for differing numbers of tables per page.

## 0.0.8 and 0.0.9

- Attempts to correct error in column renaming function application - done properly second time around.

## 0.0.7

- Corrected error in module naming convention.

## 0.0.6

- forgot to save changes to `__init__.py`.

## 0.0.5

- Corrected error in changing column names in `retrieve_panel_decisions`.
- Corrected typo in name of function `retrieve_panel_decisions`.
- Updated .ipynb file to make more compact.
- Added functions from `scraping.py` at top-level of module.

## 0.0.4

- Removed dependency on `skimpy` due to conflicts.

## 0.0.3

- Another tweak to version numbers to sort readme on TestPyPi. I promise I know what I'm doing now.

## 0.0.2

- Version tweak to fix errors in readme URLs.

## 0.0.1

- Initial release including functions to get a list of all EPSRC panels on GotW, and then to scrape the summaries of said panels' decisions.
