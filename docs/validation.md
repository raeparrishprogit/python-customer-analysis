# Validation record
Executed on October 1, 2026 with Python 3.12 and the versions in requirements.txt.

The full original dataset was processed. Assertions in build_portfolio.py stop execution if reconciliation fails. The saved notebook was executed from a fresh kernel in cell order, with actual outputs retained. Chart figures were rendered and visually inspected for labels, units, clipping, and valid denominators.

Raw records and customer-level output remain local. Published results are aggregate tables and source fingerprints. See the quality JSON in results for exact counts and source hashes.

Reproduction: install requirements, run download_data.py, then build_portfolio.py. Open analysis.ipynb and run all cells to regenerate its saved outputs. Network access is only needed for the download and package installation.
