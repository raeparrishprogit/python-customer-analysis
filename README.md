# Customer Purchasing and Segmentation Analysis
**Status: starter project / work in progress.** Includes a working cleaning and RFM summary script. Real-data findings, charts, and retention analysis are still to be completed.

## Business question
Which customer groups should a retailer consider for loyalty and win-back campaigns?

## Dataset
[UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail): UK retailer transactions from December 2010 to December 2011.
Citation: Chen, D. (2015). Online Retail. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33
The dataset is licensed CC BY 4.0. Download `Online Retail.xlsx` into `data/raw/`; it is not bundled here.

## Run
Use Python 3.10 or newer, then run from this repository's folder:
```sh
python -m pip install -r requirements.txt
python src/analyze.py
```
Outputs in `results/`:
- `quality_summary.json`: exclusions and analysis reference date.
- `customer_rfm.csv`: one row per identified customer.
- `segment_summary.csv`: customer counts and spending by segment.

Raw and generated data are excluded from version control. Publish selected aggregate charts and findings after review.

## Cleaning choices
The script checks required fields, standardizes types, removes exact duplicate rows, and excludes invalid dates, missing identifiers, cancellation invoices, nonpositive quantities, and nonpositive prices. Exclusions are counted sequentially, so each removed row is counted once.
Exact duplicate removal is an assumption: repeat identical invoice lines may be legitimate, so compare totals with and without deduplication before finalizing.
Anonymous purchases are excluded from customer analysis. Positive purchase value is **gross spend**, not net sales: refunds are not subtracted and the exclusions must be disclosed.

## RFM definitions
- Recency: days since the customer's last eligible purchase, measured from one day after the latest valid transaction date in the source.
- Frequency: number of distinct eligible invoices.
- Monetary value: sum of eligible quantity times unit price, in GBP.

Illustrative segments are evaluated in this order:
1. Loyal / recent: recency <= 90 days and frequency >= 3.
2. Lapsed repeat: recency > 90 days and frequency >= 2.
3. Recent occasional: recency <= 90 days.
4. Other / lapsed: everyone else.

These are transparent starting rules, not validated marketing thresholds. Monetary value is summarized but does not define the initial segments. Compare thresholds and investigate high-spend customers before making recommendations.

## Finish the portfolio case study
1. Run the script against the downloaded workbook.
2. Review exclusion counts and reconcile eligible spending.
3. Compare customer counts and spending across segments.
4. Create three charts: segment sizes, segment spending, and purchase-frequency distribution.
5. Add a monthly cohort retention analysis as an extension; compare cohorts only at equally observed ages.
6. Complete [the findings worksheet](docs/findings.md), then add verified findings and charts to this README.

Suggested campaign ideas are hypotheses for testing. This historical dataset alone cannot establish campaign lift, current customer value, or causes of inactivity.
