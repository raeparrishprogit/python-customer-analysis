# Findings and recommended experiment

## 1. The loyal/recent group concentrates spending
1,725 of 4,338 customers (39.76%) contribute £7,073,910.84 of £8,887,208.89 eligible gross purchase value (79.60%). Their mean invoice frequency is 8.21 and median recency is 19 days. The top 44 spenders across all segments contribute 32.06% of gross value, so averages are influenced by a small high-spend group.

**Action:** protect service quality for established repeat buyers. Avoid assuming high gross spending implies high margin; the source includes wholesalers and lacks cost information.

## 2. A defined win-back audience exists, but its size depends on the rules
602 lapsed-repeat customers have at least two observed invoices and last purchased more than 90 days before December 10, 2011. Their observed spend totals £676,302.49; mean frequency is 3.06 and median recency is 162 days.

Changing the recency boundary from 90 to 60 days increases the group to 903 customers. At 120 days it falls to 443. This supports using the rules as a starting operational definition rather than an optimized model. Full values are in `results/threshold_sensitivity.csv`.

**Experiment design:** randomly assign eligible lapsed-repeat customers to outreach or a no-outreach control, stratifying by historical spend and recency. Predefine a purchase outcome window and measure incremental purchase rate, gross margin after refunds, outreach/discount cost, and opt-outs. Choose duration and sample size from baseline behavior and the smallest commercially useful effect before launch. No campaign was run, and no uplift is claimed.

## 3. Repeat purchasing and retention answer different questions
2,845 customers (65.58%) have at least two eligible invoices somewhere in the extract. This is a history-based share with unequal exposure time.

Month-one retention measures purchasing in the next calendar month among customers grouped by their first observed purchase month. January–October 2011 cohorts contain 3,089 customers; 616 return in the next month (19.94%). This is a customer-weighted pooled rate, not an unweighted average of cohort percentages. Customers may return after skipping a month, so later cells can exceed earlier cells; this is not survival retention.

## 4. Cleaning choices are small for value but material for coverage
The raw workbook has 135,080 missing customer IDs. After deduplication, 135,037 rows are excluded for missing customer/invoice identifiers. Their behavior cannot be assigned to customers and this analysis does not represent all transactions.

Keeping exact duplicate rows instead would increase eligible gross value by £24,199.01 (approximately 0.27%) to £8,911,407.90. Duplicate removal is a documented assumption, not proof of erroneous records. Gross value excludes cancellations/refunds, so it must not be labeled net sales or profit.
