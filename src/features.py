"""Manual pandas RFM baseline and independently testable cleaning rules."""
import numpy as np
import pandas as pd
RFM=['Recency','Frequency','Monetary']
REQUIRED=['InvoiceNo','StockCode','Description','Quantity','InvoiceDate','UnitPrice','CustomerID','Country']

def clean_transactions(raw,as_of=None,window_days=365):
    missing=sorted(set(REQUIRED)-set(raw))
    if missing:raise ValueError('Missing columns: '+', '.join(missing))
    if window_days<=0:raise ValueError('window_days must be positive.')
    d=raw.copy();audit=[{'step':'Raw rows','remaining':len(d),'removed':0}]
    for c in ['Quantity','UnitPrice']:d[c]=pd.to_numeric(d[c],errors='coerce')
    d['InvoiceDate']=pd.to_datetime(d.InvoiceDate,errors='coerce')
    if d.InvoiceDate.notna().sum()==0:raise ValueError('No valid invoice dates.')
    cutoff=pd.Timestamp(as_of) if as_of is not None else d.InvoiceDate.max().normalize()+pd.Timedelta(days=1)
    start=cutoff-pd.Timedelta(days=int(window_days))
    def keep(mask,reason):
        nonlocal d
        before=len(d);d=d.loc[mask].copy();audit.append({'step':reason,'remaining':len(d),'removed':before-len(d)})
    keep(~d.duplicated(),'Remove exact duplicate lines')
    keep(d.InvoiceDate.notna() & d.Quantity.notna() & d.UnitPrice.notna() & np.isfinite(d.Quantity) & np.isfinite(d.UnitPrice),'Remove invalid dates/amounts')
    # No ID imputation: an invoice without identity cannot support member-level RFM.
    ids=pd.to_numeric(d.CustomerID,errors='coerce')
    keep(ids.notna() & np.isfinite(ids) & ids.gt(0) & ids.mod(1).eq(0),'Remove missing/invalid customer IDs')
    keep(d.InvoiceNo.notna() & d.StockCode.notna(),'Remove missing invoice/product IDs')
    d['InvoiceNo']=d.InvoiceNo.astype(str).str.strip();d['StockCode']=d.StockCode.astype(str).str.strip()
    keep(~d.InvoiceNo.str.upper().str.startswith('C'),'Exclude cancellation invoices')
    keep(d.Quantity.gt(0),'Exclude nonpositive quantities')
    keep(d.UnitPrice.gt(0),'Exclude nonpositive prices')
    # Use only the historical window. No transactions on/after as_of are allowed.
    keep(d.InvoiceDate.ge(start) & d.InvoiceDate.lt(cutoff),'Apply historical observation window')
    if d.empty:raise ValueError('No eligible purchases in the observation window.')
    d['CustomerID']=pd.to_numeric(d.CustomerID).astype('int64').astype(str)
    d['LineRevenue']=d.Quantity*d.UnitPrice
    if not np.isfinite(d.LineRevenue).all():raise ValueError('Line revenue overflow.')
    return d,pd.DataFrame(audit),cutoff

def compute_rfm(clean,as_of):
    g=clean.groupby('CustomerID',sort=True)
    # Frequency counts distinct invoices, never invoice lines or purchased units.
    r=g.agg(last_purchase=('InvoiceDate','max'),first_purchase=('InvoiceDate','min'),
        Frequency=('InvoiceNo','nunique'),Monetary=('LineRevenue','sum'),
        unique_products=('StockCode','nunique'),total_units=('Quantity','sum'))
    cutoff=pd.Timestamp(as_of)
    r['Recency']=(cutoff-r.last_purchase.dt.normalize()).dt.days
    r['first_observed_age_days']=(cutoff-r.first_purchase.dt.normalize()).dt.days
    r['average_order_value']=r.Monetary/r.Frequency
    r['units_per_order']=r.total_units/r.Frequency
    r['repeat_buyer']=r.Frequency.gt(1)
    # Modal country and top purchased SKU are descriptive lenses, not demographics
    # or validated personal interests. Stable lexical tie breaking is intentional.
    countries=clean.groupby(['CustomerID','Country'],dropna=False).size().rename('n').reset_index().sort_values(['CustomerID','n','Country'],ascending=[True,False,True]).drop_duplicates('CustomerID')
    top=clean.groupby(['CustomerID','StockCode']).Quantity.sum().reset_index().sort_values(['CustomerID','Quantity','StockCode'],ascending=[True,False,True]).drop_duplicates('CustomerID')
    r['country']=countries.set_index('CustomerID').Country
    r['top_product_code']=top.set_index('CustomerID').StockCode
    return r.reset_index()

def fit_baseline(rfm):
    """Quintile cutoffs retain ties rather than randomly splitting equal invoices."""
    cuts={c:np.quantile(rfm[c],[.2,.4,.6,.8]).tolist() for c in RFM}
    return apply_baseline(rfm,cuts),cuts

def apply_baseline(rfm,cuts):
    d=rfm.copy()
    for c,letter in zip(RFM,['R','F','M']):
        score=np.searchsorted(cuts[c],d[c].to_numpy(),side='left')+1
        d[letter+'_score']=6-score if letter=='R' else score
    d['RFM_code']=d[['R_score','F_score','M_score']].astype(str).agg(''.join,axis=1)
    # Ordered, exhaustive and mutually exclusive marketing tiers. New here means
    # first observed in this window; earlier lifetime history is unavailable.
    conditions=[(d.R_score>=4)&(d.F_score>=4)&(d.M_score>=4),
        (d.R_score<=2)&((d.F_score>=4)|(d.M_score>=4)),
        (d.R_score>=4)&(d.F_score<=2)&(d.get('first_observed_age_days',pd.Series(np.inf,index=d.index))<=60),
        (d.F_score>=3)&(d.M_score>=3),d.R_score<=2]
    names=['Champions','High value at risk of lapsing','Newly observed customers still exploring','Loyal repeat customers','Lapsed low-activity customers']
    d['baseline_tier']=np.select(conditions,names,default='Developing customers')
    if 'first_observed_age_days' in d:
        d['first_observed_age_days']=pd.to_numeric(d.first_observed_age_days,errors='coerce')
        if not np.isfinite(d.first_observed_age_days).all() or (d.first_observed_age_days<d.Recency).any():raise ValueError('First observed age must be finite and at least Recency.')
    return d

def validate_rfm(d):
    required=['CustomerID']+RFM
    if set(required)-set(d):raise ValueError('Required columns: CustomerID, Recency, Frequency, Monetary.')
    d=d.copy();d['CustomerID']=d.CustomerID.astype('string')
    if d.empty or d.CustomerID.isna().any() or d.CustomerID.str.strip().eq('').any() or not d.CustomerID.is_unique:raise ValueError('One nonmissing, unique CustomerID per row is required.')
    for c in RFM:
        d[c]=pd.to_numeric(d[c],errors='coerce')
        if not np.isfinite(d[c]).all() or d[c].lt(0).any():raise ValueError('RFM values must be finite and nonnegative.')
    if d.Frequency.lt(1).any() or d.Frequency.mod(1).ne(0).any() or d.Monetary.le(0).any():raise ValueError('Frequency must be a positive invoice count; Monetary must be positive.')
    if 'first_observed_age_days' in d:
        d['first_observed_age_days']=pd.to_numeric(d.first_observed_age_days,errors='coerce')
        if not np.isfinite(d.first_observed_age_days).all() or (d.first_observed_age_days<d.Recency).any():raise ValueError('First observed age must be finite and at least Recency.')
    return d
