# Methods and quality decisions

## Input and exclusions
Source: original UCI Online Retail.xlsx, 541,909 rows, December 1, 2010–December 9, 2011. Workbook fingerprints and all counters are in results/quality_summary.json. The UCI catalog lists no missing values, but the downloaded workbook contains 135,080 missing customer IDs and 1,454 missing descriptions. The workbook controls this analysis.

Rows are removed sequentially:

| Step | Rows removed |
|---|---:|
| Exact full-row duplicates | 5,268 |
| Invalid date | 0 |
| Missing customer or invoice ID | 135,037 |
| Invoice begins with C (cancellation) | 8,872 |
| Invalid/nonpositive quantity after prior exclusions | 0 |
| Invalid/nonpositive price | 40 |
| Remaining eligible purchases | 392,692 |

Each exclusion counter applies after earlier removals, so the counts reconcile without overlap. Missing descriptions do not automatically exclude rows. Postage/service lines are retained when they meet eligibility, so value is invoice purchase value rather than merchandise-only revenue. Cancellations/refunds are excluded rather than matched to their originating purchases. No net revenue calculation is claimed.

## RFM and segmentation
Reference date: December 10, 2011, one day after the latest valid source date. Recency uses normalized calendar dates; frequency counts distinct invoices, not item rows; monetary value sums quantity times unit price in GBP. Segments are evaluated in order: recent (<=90 days) and >=3 invoices; lapsed (>90) and >=2 invoices; remaining recent; all remaining customers. Thresholds are illustrative and tested at 60/90/120 days. Monetary value does not determine initial segment assignment.

Customer IDs are treated as identifiers. The source contains no customer-level purchase histories before December 2010. Older cohorts have more opportunity to accumulate invoices and spending; no segment comparison is presented as causal.

## Cohort construction
Deduplicate eligible customer/invoice pairs, map each customer to their first observed purchase month, and count distinct customers purchasing at each calendar-month age. The denominator remains the original cohort size. Explicitly include zero-activity months once they are observable. Do not fill future cells with zeros. Use only calendar months through November 2011 because December 2011 is partial. Exclude the initial December 2010 cohort from the pooled month-one rate; it remains visible and flagged in the heatmap. Actual first-ever purchase dates are unknown even for later cohorts.

## Reconciliation and sensitivity
Input rows equal eligible rows plus sequential removals. Row-level gross value equals customer totals and segment totals. Distinct customer/invoice pairs equal the sum of per-customer frequency. Segment counts sum to 4,338 customers. The duplicate-retention scenario recomputes eligible spending before deduplication; it does not infer which individual duplicate was erroneous.

These descriptive calculations cover the extract and do not estimate uncertainty about a future population. Business outcomes require a randomized or otherwise defensible causal evaluation; no predicted uplift or customer lifetime value is estimated.
