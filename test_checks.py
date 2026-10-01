import pandas as pd
from src import analyze as py
rows = [['1','P',2,'2011-01-01',10,'A'], ['2','P',1,'2011-01-02',10,'A'], ['3','P',1,'2011-12-01',20,'B'], ['3','P',1,'2011-12-01',20,'B'], ['C4','P',1,'2011-12-02',20,'B'], ['5','P',-1,'2011-12-03',20,'B'], ['6','P',1,'2011-12-04',20,None]]
rfm, summary, quality = py.analyze(pd.DataFrame(rows, columns=py.REQUIRED))
assert rfm.loc['A','frequency'] == 2
assert rfm.loc['A','monetary_gbp'] == 30
assert rfm.loc['A','segment'] == 'Lapsed repeat'
assert rfm.loc['B','recency_days'] == 4
assert quality['eligible_rows'] == 3
assert quality['exact_duplicate_rows_removed'] == 1
assert quality['eligible_gross_purchase_value_gbp'] == 50
assert summary.gross_purchase_value_gbp.sum() == 50

try:
    py.analyze(pd.DataFrame(columns=['InvoiceNo']))
except ValueError:
    pass
else:
    raise AssertionError('Missing fields must fail')
print('PASS: customer exclusions, gross value, invoice counts, recency, segmentation, and schema guard')
