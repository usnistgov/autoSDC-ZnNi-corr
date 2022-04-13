Development of an Automated Millifluidic Platform and Data-Analysis Pipeline for Rapid Electrochemical Corrosion Measurements: A Ph Study on Zn-Ni
===================================================================

This is a paper companion repository containing data analysis and visualization code reproducing the analysis in [our Zn-Ni pH series work](https://dx.doi.org/10.2139/ssrn.4075907).

To process the raw electrochemical data and generate a table of results:
```sh
python scripts/generate_report.py
```
Jupyter notebooks with data wrangling and plotting code are provided in the notebooks folder.

## Contact Information
- Howie Joress, @hjoress
- Brian DeCost, @bdecost


## Related Material


## Cite This Work

<!-- Please provide a DOI, URL, and suggested citation. -->


## Third-Party Dependencies
We're currently using [git-subrepo](https://github.com/ingydotnet/git-subrepo) to include shared automation and data analysis libraries.

These include:
- [./autoSDC] our scanning droplet cell library (https://github.com /usnistgov/autoSDC)

- [./tafel-fitter] Tafel analysis library (https://github.com/usnistgov/tafel-fitter, which is a fork of https://github.com/MEG-LBNL/Tafel_Fitter).

This repository is subject to the [NIST Disclaimer of Warranty](LICENSE.md).
