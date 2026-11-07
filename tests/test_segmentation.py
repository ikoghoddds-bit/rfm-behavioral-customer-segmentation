from pathlib import Path
import json
import numpy as np
import pandas as pd
import pytest
from src.features import clean_transactions,compute_rfm,fit_baseline,apply_baseline,validate_rfm,RFM
from src.segment import elbow_k
from src.predict import assign_segments
ROOT=Path(__file__).resolve().parents[1]

def test_cleaning_and_manual_rfm():
    def row(invoice,sku,qty,date,price,cid):return dict(InvoiceNo=invoice,StockCode=sku,Description='Item',Quantity=qty,InvoiceDate=date,UnitPrice=price,CustomerID=cid,Country='UK')
    rows=[row('A','x',2,'2011-01-10',5,1),row('A','y',1,'2011-01-10',10,1),row('B','z',3,'2011-01-05',5,1),
        row('C1','x',-2,'2011-01-10',5,1),row('D','x',1,'2011-01-10',0,1),row('E','x',1,'2011-01-10',5,None),
        row('F','x',1,'2011-01-11',5,1),row('G','x',1,'2010-01-01',5,1)]
    rows.append(rows[0].copy())
    cleaned,audit,as_of=clean_transactions(pd.DataFrame(rows),as_of='2011-01-11',window_days=30)
    assert len(cleaned)==3 and audit.removed.sum()+len(cleaned)==len(rows)
    r=compute_rfm(cleaned,as_of).iloc[0]
    assert r.Recency==1 and r.Frequency==2 and r.Monetary==35
    assert r.average_order_value==17.5 and r.unique_products==3

def test_baseline_ties_and_coverage():
    x=pd.DataFrame({'CustomerID':list('abcde'),'Recency':[1,1,10,50,100],'Frequency':[1,1,2,5,10],'Monetary':[10,10,30,100,500],'first_observed_age_days':[1,1,100,100,200]})
    scored,cuts=fit_baseline(x)
    assert scored.loc[0,['R_score','F_score','M_score']].tolist()==scored.loc[1,['R_score','F_score','M_score']].tolist()
    assert not scored.baseline_tier.isna().any()
    assert scored[['R_score','F_score','M_score']].ge(1).all().all() and scored[['R_score','F_score','M_score']].le(5).all().all()
    unknown=apply_baseline(x.drop(columns='first_observed_age_days'),cuts)
    assert not unknown.baseline_tier.str.startswith('New').any()

def test_elbow_definition():
    k,distance=elbow_k([1,2,3,4,5],[1000,450,200,150,120])
    assert k==3 and len(distance)==5
    with pytest.raises(ValueError):elbow_k([1,2],[100,50])

def test_exports_reconcile_and_model_round_trip():
    d=pd.read_csv(ROOT/'outputs/customer_segments.csv',dtype={'CustomerID':'string'})
    p=pd.read_csv(ROOT/'outputs/segment_profiles.csv');m=json.loads((ROOT/'outputs/metrics.json').read_text())
    assert d.CustomerID.is_unique and len(d)==m['customers']==p.customers.sum()
    assert d.segment.nunique()==m['selected_k'] and p.segment.is_unique
    assert d.Monetary.sum()==pytest.approx(m['gross_purchase_value_gbp'])
    assert p.value_share.sum()==pytest.approx(1)
    predicted=assign_segments(d[['CustomerID']+RFM])
    assert predicted.segment.tolist()==d.segment.tolist()
    assert predicted.distance_to_center.ge(0).all()

def test_schema_and_invalid_inputs():
    d=pd.read_csv(ROOT/'data/example_rfm.csv',dtype={'CustomerID':'string'})
    for col,val in [('Monetary',-1),('Frequency',1.5),('Recency',np.inf),('CustomerID','')]:
        bad=d.copy();bad[col]=bad[col].astype(object);bad.loc[0,col]=val
        with pytest.raises(ValueError):validate_rfm(bad)
    with pytest.raises(ValueError):validate_rfm(d.drop(columns='Monetary'))
    with pytest.raises(ValueError):validate_rfm(pd.concat([d.head(1)]*2))
