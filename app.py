"""Run locally: python -m streamlit run app.py"""
from pathlib import Path
import json
import pandas as pd
import streamlit as st
from src.predict import assign_segments
ROOT=Path(__file__).parent
st.set_page_config(page_title='RFM & Behavioral Customer Segmentation',page_icon='◈',layout='wide')
# Native theme controls text and surfaces together; no forced pale canvas under
# a viewer's dark theme. This keeps labels, controls and tables readable.
st.markdown('''<style>div[data-testid="stMetric"]{padding:16px;border:1px solid rgba(128,128,128,.35);border-top:3px solid #087e8b;border-radius:12px}</style>''',unsafe_allow_html=True)
st.caption('JOSEPH IKOGHO · DATA SCIENCE PORTFOLIO / 02')
st.title('RFM & Behavioral Customer Segmentation')
st.write('Turn transaction history into distinct customer groups and targeted campaign hypotheses.')
if not (ROOT/'outputs/metrics.json').exists():st.error('Run python -m src.segment first.');st.stop()
@st.cache_data
def load():
    return (pd.read_csv(ROOT/'outputs/customer_segments.csv',dtype={'CustomerID':'string'}),pd.read_csv(ROOT/'outputs/segment_profiles.csv'),pd.read_csv(ROOT/'outputs/campaign_playbook.csv'))
d,profiles,playbook=load();m=json.loads((ROOT/'outputs/metrics.json').read_text())
with st.sidebar:
    st.header('Audience filters')
    names=sorted(d.segment.unique());selected=st.multiselect('K-Means segments',names,default=names)
    baselines=st.multiselect('Manual RFM tiers',sorted(d.baseline_tier.unique()),default=sorted(d.baseline_tier.unique()))
    country=st.selectbox('Country',['All countries']+sorted(d.country.dropna().unique()))
    st.caption('Filters select an existing audience; they do not refit clusters or change k.')
    st.divider();st.write(f'Frozen snapshot: {m["as_of"]}\n\nLookback: {m["window_days"]} days\n\nCurrency: GBP (£)')
view=d[d.segment.isin(selected)&d.baseline_tier.isin(baselines)]
if country!='All countries':view=view[view.country==country]
a,b,c,e=st.columns(4)
a.metric('Customers in audience',f'{len(view):,}');b.metric('K-Means segments',str(m['selected_k']));c.metric('Historical purchase value',f'£{view.Monetary.sum():,.0f}');e.metric('Median recency',f'{view.Recency.median():.0f} days' if len(view) else '—')
st.caption('Public UCI Online Retail data · historical purchase value excludes cancellations/returns and is not net revenue, profit or future lifetime value. No conversion uplift is claimed.')
tabs=st.tabs(['Segment overview','Manual RFM baseline','Campaign playbook','Audience export','Why this k?','Assign an RFM CSV'])
with tabs[0]:
    st.subheader('Understand each group in business terms')
    st.dataframe(profiles[['segment','customers','customer_share','value_share','Recency_median','Frequency_median','Monetary_median','average_order_value_median','unique_products_median','repeat_buyer_share']],hide_index=True,width='stretch')
    st.caption('Profiles describe the full modeling population; audience filters affect the charts and export below.')
    if len(view):
        st.bar_chart(view.groupby('segment').size().rename('Customers'))
        st.scatter_chart(view,x='Recency',y='Monetary',color='segment')
    else:st.info('No customers match these filters.')
    st.write('Behavioral lenses: repeat purchasing, order value, units per basket, product breadth, first observed purchase age, modal country and top purchased SKU. Only RFM enters K-Means; the other fields describe and activate the segments.')
    st.warning('Wholesalers are present in this retailer. Large baskets may reflect business purchasing rather than household wealth. No household, demographic, browsing or consent fields are available.')
with tabs[1]:
    st.subheader('RFM calculated manually in pandas')
    st.write('Recency = days since last eligible purchase; Frequency = distinct invoices in the 365-day window; Monetary = sum of positive quantity × price in GBP. Lower Recency is better; higher Frequency and Monetary are better.')
    st.write('Each metric receives a 1–5 score using population quintile cutoffs; recency is reversed. Identical values keep identical scores, so tied invoice counts can create unequal tier sizes. Ordered rules assign Champions, at-risk high-value, new, loyal, lapsed or developing customers before K-Means is fitted.')
    st.dataframe(pd.read_csv(ROOT/'outputs/baseline_counts.csv'),hide_index=True)
    st.subheader('How the intuitive baseline compares with clustering')
    st.dataframe(pd.read_csv(ROOT/'outputs/baseline_vs_clusters.csv'),hide_index=True,width='stretch')
    st.caption('Neither method is ground truth. K-Means may combine or split manual tiers; disagreement is a diagnostic, not a classification error.')
    st.subheader('Cleaning audit')
    st.dataframe(pd.read_csv(ROOT/'outputs/cleaning_audit.csv'),hide_index=True)
with tabs[2]:
    st.subheader('Different groups, different campaign hypotheses')
    for row in playbook.to_dict('records'):
        with st.expander(row['segment']+' · '+row['campaign']):
            st.write(row['message_or_offer']);st.write('Measure: '+row['primary_kpi']);st.caption(row['guardrail'])
    st.info('Activation overlays: manual high-value-at-risk customers receive a personalized win-back hypothesis even inside a broad low-value cluster; newly observed manual tiers receive a second-purchase onboarding hypothesis. See recommended_campaign in the audience export.')
    st.download_button('Download campaign playbook',playbook.to_csv(index=False),'campaign_playbook.csv','text/csv')
    st.subheader('Plan an experiment, not an assumed uplift')
    st.write('Randomize eligible, consented customers within each segment to a segment-specific treatment or control. Compare conversion and contribution over a prespecified horizon. Set sample size using baseline conversion and a minimum detectable effect; account for multiple segment tests. Track treatment exposure and offer redemption.')
    contact=st.number_input('Planning cost per contacted customer (£)',0.,100.,.20,.05)
    st.metric('Cost to contact the filtered audience',f'£{len(view)*contact:,.2f}')
    st.caption('A budget estimate only. The dataset contains no campaign/control outcomes, marketing permissions, margin or verified incremental conversions.')
    st.subheader('What broader data could add')
    st.write('Opt-in clickstream and category browsing could add engagement/interest lenses. Authorized household or lifecycle data could support household-level analysis. Product taxonomy could replace crude SKU affinity. Test incremental usefulness and fairness; do not infer household composition or personal interests from purchases alone.')
with tabs[3]:
    st.subheader('Export a named audience')
    st.dataframe(view[['CustomerID','segment','baseline_tier','RFM_code','Recency','Frequency','Monetary','average_order_value','unique_products','first_observed_age_days','country','top_product_code','recommended_campaign']],hide_index=True,width='stretch')
    st.download_button('Download filtered audience',view.to_csv(index=False),'segmented_audience.csv','text/csv')
    st.caption('Public pseudonymous IDs, not a production contact list. Real activation requires authorized identity resolution and contact permissions.')
with tabs[4]:
    st.subheader('Elbow evidence and robustness')
    elbow=pd.read_csv(ROOT/'outputs/elbow_diagnostics.csv')
    st.line_chart(elbow.set_index('k')[['inertia']]);st.dataframe(elbow,hide_index=True)
    st.write(f'For k=1…10, the largest distance below the normalized endpoint chord selects k={m["selected_k"]}. This reproducible elbow heuristic supports a practical candidate; it does not prove a unique natural number of customer types. Restricting the candidate range to 1…8 yields k={m["elbow_k_range_1_to_8"]}.')
    st.write(f'Sampled silhouette at selected k: {m["silhouette_sampled"]:.3f}. Minimum repeated-seed ARI: {m["seed_ari_min"]:.3f}; 99th-percentile-capping ARI versus main model: {m["capped_99pct_ari"]:.3f}. These are diagnostics, not accuracy or conversion outcomes.')
    st.image(str(ROOT/'outputs/segmentation_evidence.png'))
    st.caption('Log1p reduces long monetary/frequency tails; StandardScaler prevents raw GBP from dominating distance. No main-model winsorization. PCA is a projection of the three transformed inputs and can hide overlap.')
with tabs[5]:
    st.subheader('Assign comparable customer RFM to frozen segments')
    st.write('Upload CustomerID, Recency (days), Frequency (distinct invoices), Monetary (GBP), calculated using the same 365-day definitions. This does not retrain the model. New periods or businesses require validation; no automatic domain compatibility is assumed.')
    st.download_button('Download example RFM',(ROOT/'data/example_rfm.csv').read_bytes(),'example_rfm.csv','text/csv')
    upload=st.file_uploader('RFM CSV',type='csv')
    if upload is not None:
        try:
            result=assign_segments(pd.read_csv(upload,dtype={'CustomerID':'string'}));st.dataframe(result,hide_index=True,width='stretch')
            st.download_button('Download assignments',result.to_csv(index=False),'assigned_segments.csv','text/csv')
            st.caption('A baseline “new” tier requires optional first_observed_age_days; it is not assigned when that history is unavailable. distance_to_center is a relative diagnostic, not confidence or probability.')
        except (ValueError,TypeError,KeyError) as exc:st.error(str(exc))
st.divider();st.caption('Designed by Nova Agentic · Portfolio by Joseph Ikogho · UCI Online Retail · No campaigns sent')
