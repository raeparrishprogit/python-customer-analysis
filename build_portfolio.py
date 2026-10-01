"""Rebuild the complete customer case study from the original UCI workbook."""
import hashlib
import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from src.analyze import analyze, clean_purchases

ROOT = Path(__file__).resolve().parent
BLUE, GOLD = '#245A81', '#C48A22'

def build(raw=None):
    source = ROOT / 'data/raw/Online Retail.xlsx'
    if raw is None:
        raw = pd.read_excel(source, dtype={'InvoiceNo':'string','CustomerID':'string','StockCode':'string'})
    result = ROOT / 'results'
    result.mkdir(exist_ok=True)
    rfm, segments, quality = analyze(raw)
    clean, _, reference = clean_purchases(raw)
    kept, _, _ = clean_purchases(raw, deduplicate=False)
    # Independent row-level sum reconciles to both customer and segment totals.
    gross = float(clean.purchase_value_gbp.sum())
    assert np.isclose(gross, rfm.monetary_gbp.sum())
    assert np.isclose(gross, segments.gross_purchase_value_gbp.sum())
    assert len(rfm) == segments.customers.sum()
    assert len(raw) == len(clean) + sum(v for k,v in quality.items() if k.endswith('_rows_removed'))
    orders = clean[['CustomerID','InvoiceNo','InvoiceDate']].drop_duplicates(['CustomerID','InvoiceNo'])
    assert len(orders) == rfm.frequency.sum()
    segments['customer_share_pct'] = 100 * segments.customers / len(rfm)
    segments['spend_share_pct'] = 100 * segments.gross_purchase_value_gbp / gross
    segments['average_customer_spend_gbp'] = segments.gross_purchase_value_gbp / segments.customers
    segments.to_csv(result/'segment_summary.csv')
    # Individual customer rows stay local; only aggregate evidence is published.
    rfm.to_csv(result/'customer_rfm.csv')
    orders['month'] = orders.InvoiceDate.dt.to_period('M')
    orders['cohort'] = orders.groupby('CustomerID')['month'].transform('min')
    orders['age'] = (orders.month.dt.year-orders.cohort.dt.year)*12 + orders.month.dt.month-orders.cohort.dt.month
    # December 2011 is incomplete. Compare only fully observed calendar months.
    last_complete = raw.InvoiceDate.max().to_period('M') - 1
    complete = orders[orders.month <= last_complete].copy()
    sizes = complete.groupby('cohort').CustomerID.nunique()
    observed = complete.groupby(['cohort','age']).CustomerID.nunique()
    records = []
    for cohort, size in sizes.items():
        max_age = (last_complete.year-cohort.year)*12 + last_complete.month-cohort.month
        for age in range(max_age+1):
            active = int(observed.get((cohort,age),0))
            records.append([str(cohort),age,int(size),active,100*active/size])
    cohorts = pd.DataFrame(records, columns=['cohort','age_month','cohort_customers','active_customers','retention_pct'])
    cohorts.to_csv(result/'cohort_retention.csv',index=False)
    sensitivity=[]
    for cutoff in [60,90,120]:
        labels=np.select([(rfm.recency_days<=cutoff)&(rfm.frequency>=3), (rfm.recency_days>cutoff)&(rfm.frequency>=2), rfm.recency_days<=cutoff],['Loyal / recent','Lapsed repeat','Recent occasional'],default='Other / lapsed')
        temp=rfm.assign(segment=labels).groupby('segment').agg(customers=('frequency','size'),gross_spend_gbp=('monetary_gbp','sum')).reset_index()
        temp['recency_cutoff_days']=cutoff
        sensitivity.append(temp)
    pd.concat(sensitivity).to_csv(result/'threshold_sensitivity.csv',index=False)
    frequency=rfm.frequency.map(lambda n:'1' if n==1 else '2' if n==2 else '3–5' if n<=5 else '6–10' if n<=10 else '11+')
    frequency.value_counts().reindex(['1','2','3–5','6–10','11+'],fill_value=0).rename_axis('distinct_invoices').to_csv(result/'purchase_frequency.csv',header=['customers'])
    top_count=max(1,int(np.ceil(len(rfm)*.01)))
    m1=cohorts[(cohorts.age_month==1)&(cohorts.cohort!='2010-12')]
    quality.update(source_start=str(raw.InvoiceDate.min()),source_end=str(raw.InvoiceDate.max()),
      raw_missing_customer_ids=int(raw.CustomerID.isna().sum()),
      eligible_distinct_invoices=len(orders), repeat_customers=int((rfm.frequency>=2).sum()),
      repeat_customer_pct=float(100*(rfm.frequency>=2).mean()),
      gross_without_deduplication_gbp=float(kept.purchase_value_gbp.sum()),
      deduplication_spend_difference_gbp=float(kept.purchase_value_gbp.sum()-gross),
      top_one_percent_customer_count=top_count,
      top_one_percent_spend_share_pct=float(100*rfm.monetary_gbp.nlargest(top_count).sum()/gross),
      pooled_month_one_retention_pct=float(100*m1.active_customers.sum()/m1.cohort_customers.sum()),
      month_one_cohort_customers=int(m1.cohort_customers.sum()),month_one_returning_customers=int(m1.active_customers.sum()),
      cohort_last_complete_month=str(last_complete), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
      analysis_date='2026-10-01',validation='PASS: exclusions, distinct invoices, customer counts and spend reconcile')
    (result/'quality_summary.json').write_text(json.dumps(quality,indent=2),encoding='utf-8')
    return quality

def charts():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    out=ROOT/'charts';out.mkdir(exist_ok=True)
    s=pd.read_csv(ROOT/'results/segment_summary.csv').sort_values('customers')
    figs=[]
    for measure,title,unit,name in [('customers','Customer groups at the dataset endpoint','Customers','customer_segments'),('gross_purchase_value_gbp','Recorded purchase value by customer group','Gross purchase value (GBP; refunds excluded)','segment_spending')]:
        fig,ax=plt.subplots(figsize=(10,5.6));ax.barh(s.segment,s[measure],color=BLUE)
        ax.set(xlabel=unit,title=title);ax.xaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{x:,.0f}'))
        ax.set_xlim(0,s[measure].max()*1.2)
        for i,v in enumerate(s[measure]):ax.text(v+s[measure].max()*.015,i,f'{v:,.0f}',va='center')
        fig.text(.02,.02,'UCI Online Retail • Identified customers with eligible purchases • Dec 2010–Dec 9, 2011',fontsize=9,color='#555555')
        fig.tight_layout(rect=[0,.06,1,1]);fig.savefig(out/f'{name}.svg');fig.savefig(out/f'{name}.png',dpi=140);figs.append(fig)
    freq=pd.read_csv(ROOT/'results/purchase_frequency.csv')
    fig,ax=plt.subplots(figsize=(10,5.6));ax.bar(freq.distinct_invoices,freq.customers,color=BLUE)
    ax.set(title='Purchase frequency across the observed history',xlabel='Distinct eligible invoices per customer',ylabel='Customers')
    for i,v in enumerate(freq.customers):ax.text(i,v+20,f'{v:,}',ha='center')
    ax.set_ylim(0,freq.customers.max()*1.15)
    fig.text(.02,.02,'UCI Online Retail • Observation time differs by first purchase date; this is not a retention rate.',fontsize=9,color='#555555')
    fig.tight_layout(rect=[0,.06,1,1]);fig.savefig(out/'purchase_frequency.svg');fig.savefig(out/'purchase_frequency.png',dpi=140);figs.append(fig)
    c=pd.read_csv(ROOT/'results/cohort_retention.csv')
    matrix=c.pivot(index='cohort',columns='age_month',values='retention_pct')
    fig,ax=plt.subplots(figsize=(11,7));im=ax.imshow(np.ma.masked_invalid(matrix.to_numpy()),cmap='Blues',vmin=0,vmax=100,aspect='auto')
    ax.set_xticks(range(len(matrix.columns)),matrix.columns);ax.set_yticks(range(len(matrix.index)),matrix.index)
    ax.set(title='Monthly customer retention by first observed purchase',xlabel='Months since first observed purchase',ylabel='First observed purchase month')
    for i in range(len(matrix)):
        for j in range(len(matrix.columns)):
            v=matrix.iloc[i,j]
            if pd.notna(v):ax.text(j,i,f'{v:.0f}%',ha='center',va='center',fontsize=9,color='white' if v>60 else '#222222')
    fig.colorbar(im,ax=ax,label='Customers purchasing / original cohort (%)',shrink=.8)
    fig.text(.02,.025,'Through Nov 2011 only • Blank = not yet observed • Dec 2010 cohort includes pre-existing customers',fontsize=9,color='#555555')
    fig.tight_layout(rect=[0,.06,1,1]);fig.savefig(out/'cohort_retention.svg');fig.savefig(out/'cohort_retention.png',dpi=140);figs.append(fig)
    return figs

if __name__=='__main__':
    print(json.dumps(build(),indent=2))
    charts()
