"""Stakeholder presentation helpers; original model/CSV field names stay stable."""
import re
import pandas as pd

SEGMENT_ORDER = ['Loyal high-value customers', 'Active developing customers', 'Lapsed occasional customers']
SEGMENT_COLORS = dict(zip(SEGMENT_ORDER, ['#087F83', '#1D4ED8', '#B45309']))
SHORT_SEGMENTS = dict(zip(SEGMENT_ORDER, ['Loyal High-Value', 'Active Developing', 'Lapsed Occasional']))
SHORT_TIERS = {
    'Champions': 'Champions', 'Developing customers': 'Developing',
    'High value at risk of lapsing': 'High Value At Risk',
    'Lapsed low-activity customers': 'Lapsed Low-Activity',
    'Loyal repeat customers': 'Loyal Repeat',
    'Newly observed customers still exploring': 'Newly Observed',
}

def title_case(text):
    """Capitalize each word without damaging RFM, CSV, GBP, SKU or K-Means."""
    return re.sub(r'(^|[\s/\-])([a-z])', lambda m: m[1] + m[2].upper(), str(text))


def filter_audience(customers, segments, tiers, country='All Countries'):
    view = customers[customers.segment.isin(segments) & customers.baseline_tier.isin(tiers)]
    return view.copy() if country == 'All Countries' else view[view.country.eq(country)].copy()


def summarize_audience(view):
    """Shares and medians use exactly the filtered audience, including zero rows."""
    cols = ['segment','customers','customer_share','purchase_value','value_share',
            'Recency_median','Frequency_median','Monetary_median','average_order_value_median',
            'unique_products_median','units_per_order_median','first_observed_age_days_median','repeat_buyer_share']
    if view.empty:
        return pd.DataFrame(columns=cols)
    out = view.groupby('segment', sort=False).agg(
        customers=('CustomerID','size'), purchase_value=('Monetary','sum'),
        Recency_median=('Recency','median'), Frequency_median=('Frequency','median'),
        Monetary_median=('Monetary','median'), average_order_value_median=('average_order_value','median'),
        unique_products_median=('unique_products','median'), units_per_order_median=('units_per_order','median'),
        first_observed_age_days_median=('first_observed_age_days','median'), repeat_buyer_share=('repeat_buyer','mean'),
    ).reset_index()
    out['customer_share'] = out.customers / len(view)
    out['value_share'] = out.purchase_value / view.Monetary.sum()
    order = {name:i for i,name in enumerate(SEGMENT_ORDER)}
    return out.assign(_order=out.segment.map(order).fillna(len(order))).sort_values('_order').drop(columns='_order')[cols].reset_index(drop=True)


def scatter_audience(view, zoom=False, quantile=.99):
    """Crop only the scatter view; never mutate modeling, KPI or export data."""
    if view.empty or not zoom:
        return view.copy(), None, 0
    cutoff = float(view.Monetary.quantile(quantile))
    plotted = view[view.Monetary <= cutoff].copy()
    return plotted, cutoff, len(view)-len(plotted)


PROFILE_LABELS = {
    'segment':'Customer Segment', 'customers':'Customers', 'customer_share':'Customer Share',
    'purchase_value':'Historical Purchase Value (£)', 'value_share':'Purchase-Value Share',
    'Recency_median':'Median Days Since Purchase', 'Frequency_median':'Median Orders',
    'Monetary_median':'Median Customer Purchase Value (£)',
    'average_order_value_median':'Median Order Value (£)', 'unique_products_median':'Median Product Breadth',
    'units_per_order_median':'Median Units Per Order', 'first_observed_age_days_median':'Median Days Since First Observed Purchase',
    'repeat_buyer_share':'Repeat-Buyer Share',
}
AUDIENCE_LABELS = {
    'CustomerID':'Customer ID', 'segment':'Customer Segment', 'baseline_tier':'Manual RFM Tier',
    'RFM_code':'RFM Code', 'Recency':'Days Since Purchase', 'Frequency':'Orders',
    'Monetary':'Historical Purchase Value (£)', 'average_order_value':'Average Order Value (£)',
    'unique_products':'Product Breadth', 'first_observed_age_days':'Days Since First Observed Purchase',
    'country':'Country', 'top_product_code':'Top Purchased SKU', 'recommended_campaign':'Recommended Campaign',
    'cluster_id':'Internal Cluster ID', 'distance_to_center':'Distance To Cluster Center',
    'R_score':'R Score', 'F_score':'F Score', 'M_score':'M Score',
}


def humanize_frame(frame, labels):
    d=frame.copy()
    for c in ['segment','baseline_tier','recommended_campaign']:
        if c in d: d[c]=d[c].map(title_case)
    return d.rename(columns={c:labels.get(c,title_case(str(c).replace('_',' '))) for c in d.columns})
