"""Produce auditable purchase-based customer summaries from UCI Online Retail."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["InvoiceNo", "StockCode", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID"]

def clean_purchases(raw, deduplicate=True):
    missing = set(REQUIRED) - set(raw.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    df = raw.copy()
    quality = {"input_rows": len(df)}
    quality["exact_duplicate_rows_removed"] = int(df.duplicated().sum()) if deduplicate else 0
    if deduplicate:
        df = df.drop_duplicates().copy()
    for col in ("InvoiceNo", "CustomerID"):
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    for col in ("Quantity", "UnitPrice"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    latest = df["InvoiceDate"].max()
    if pd.isna(latest):
        raise ValueError("No valid dates in the source.")
    reference = latest.normalize() + pd.Timedelta(days=1)
    conditions = [
        ("invalid_date", lambda d: d["InvoiceDate"].isna()),
        ("missing_customer_or_invoice", lambda d: d["CustomerID"].isna() | d["InvoiceNo"].isna()),
        ("cancellation", lambda d: d["InvoiceNo"].str.upper().str.startswith("C").fillna(False)),
        ("invalid_quantity", lambda d: d["Quantity"].isna() | (d["Quantity"] <= 0) | d["Quantity"].isin([float("inf"), -float("inf")])),
        ("invalid_price", lambda d: d["UnitPrice"].isna() | (d["UnitPrice"] <= 0) | d["UnitPrice"].isin([float("inf"), -float("inf")])),
    ]
    for name, condition in conditions:
        mask = condition(df)
        quality[name + "_rows_removed"] = int(mask.sum())
        df = df.loc[~mask].copy()
    if df.empty:
        raise ValueError("No eligible purchases remain after cleaning.")
    df["purchase_value_gbp"] = df["Quantity"] * df["UnitPrice"]
    return df, quality, reference

def analyze(raw):
    df, quality, reference = clean_purchases(raw)
    rfm = df.groupby("CustomerID").agg(
        last_purchase=("InvoiceDate", "max"),
        frequency=("InvoiceNo", "nunique"),
        monetary_gbp=("purchase_value_gbp", "sum"),
    )
    rfm["recency_days"] = (reference - rfm["last_purchase"].dt.normalize()).dt.days
    def segment(row):
        if row.recency_days <= 90 and row.frequency >= 3:
            return "Loyal / recent"
        if row.recency_days > 90 and row.frequency >= 2:
            return "Lapsed repeat"
        if row.recency_days <= 90:
            return "Recent occasional"
        return "Other / lapsed"
    rfm["segment"] = rfm.apply(segment, axis=1)
    summary = rfm.groupby("segment").agg(
        customers=("frequency", "size"),
        gross_purchase_value_gbp=("monetary_gbp", "sum"),
        average_frequency=("frequency", "mean"),
        median_recency_days=("recency_days", "median"),
    )
    quality.update(eligible_rows=len(df), identified_customers=len(rfm),
                   reference_date=str(reference.date()),
                   eligible_gross_purchase_value_gbp=float(df["purchase_value_gbp"].sum()))
    return rfm, summary, quality

def main():
    source = ROOT / "data" / "raw" / "Online Retail.xlsx"
    if not source.is_file():
        raise SystemExit(f"Download the UCI workbook first: {source}")
    raw = pd.read_excel(source, dtype={"InvoiceNo": "string", "CustomerID": "string", "StockCode": "string"})
    rfm, summary, quality = analyze(raw)
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    rfm.to_csv(output / "customer_rfm.csv")
    summary.to_csv(output / "segment_summary.csv")
    (output / "quality_summary.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
    print("Done. Review results/quality_summary.json before interpreting the summaries.")

if __name__ == "__main__":
    main()
