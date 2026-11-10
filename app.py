"""Run locally: python -m streamlit run app.py. Presentation-only release 1.1."""
from pathlib import Path
from html import escape
import json
import pandas as pd
import streamlit as st
from src.predict import assign_segments
from src.presentation import (title_case as tc,filter_audience,summarize_audience,scatter_audience,
    SEGMENT_ORDER,SEGMENT_COLORS,SHORT_SEGMENTS,SHORT_TIERS,PROFILE_LABELS,AUDIENCE_LABELS,humanize_frame)
from src.dashboard_charts import count_chart,share_chart,scatter_chart
ROOT=Path(__file__).parent
st.set_page_config(page_title='RFM & Behavioral Customer Segmentation',page_icon='◈',layout='wide')
# Native foreground/background colors remain paired in either theme. The image
# supplied by the user was zoomed out; normal-size typography stays restrained.
st.markdown('''<style>
.block-container{padding-top:2.25rem;max-width:1600px}
@media(min-width:900px){section[data-testid="stSidebar"][aria-expanded="true"]{min-width:320px;max-width:370px}}
div[data-testid="stMetric"]{padding:16px;border:1px solid rgba(128,128,128,.35);border-top:3px solid #087f83;border-radius:12px}
.snapshot-band{padding:.75rem 1rem;border:1px solid rgba(128,128,128,.4);border-radius:10px;margin:.5rem 0 1.2rem;font-size:.95rem}
.segment-heading{padding-left:.8rem;border-left:5px solid;min-height:3.5rem}
.segment-heading h3{font-size:1.3rem;line-height:1.35;margin:.2rem 0 .8rem}
div[data-testid="stCaptionContainer"]{font-size:.9rem}
</style>''',unsafe_allow_html=True)
if not (ROOT/'outputs/metrics.json').exists():st.error('Run python -m src.segment first.');st.stop()
@st.cache_data
def load():
    return (pd.read_csv(ROOT/'outputs/customer_segments.csv',dtype={'CustomerID':'string'}),
        pd.read_csv(ROOT/'outputs/campaign_playbook.csv'))
d,playbook=load();m=json.loads((ROOT/'outputs/metrics.json').read_text())
names=[n for n in SEGMENT_ORDER if n in d.segment.unique()]
tiers=sorted(d.baseline_tier.unique());all_countries=['All Countries']+sorted(d.country.dropna().unique())
PAGES=['Segment Overview','Manual RFM Baseline','Campaign Playbook','Audience Export','Cluster Evidence','Assign An RFM CSV']
for key,value in [('segments',names),('tiers',tiers),('country','All Countries'),('workspace',PAGES[0])]:
    if key not in st.session_state:st.session_state[key]=value

def select_all():st.session_state.update(segments=names.copy(),tiers=tiers.copy())
def clear_filters():st.session_state.update(segments=[],tiers=[])
def reset_filters():st.session_state.update(segments=names.copy(),tiers=tiers.copy(),country='All Countries')
def focus_segment(name):st.session_state.update(segments=[name],workspace='Audience Export')

with st.sidebar:
    st.header('Audience Filters')
    x,y,z=st.columns(3)
    x.button('Select All',on_click=select_all,width='stretch',help='Select all segments and manual tiers; keep the country filter.')
    y.button('Clear',on_click=clear_filters,width='stretch',help='Clear the segment and manual-tier selections.')
    z.button('Reset',on_click=reset_filters,width='stretch',help='Restore all segments, all tiers and all countries.')
    selected=st.multiselect('Customer Segments',names,key='segments',format_func=lambda s:SHORT_SEGMENTS.get(s,tc(s)),help='Short filter labels refer to the full named segments in the overview. Filters do not refit K-Means.')
    baseline=st.multiselect('Manual RFM Tiers',tiers,key='tiers',format_func=lambda s:SHORT_TIERS.get(s,tc(s)))
    country=st.selectbox('Country',all_countries,key='country')
    st.caption('All audience metrics, profiles, charts and exports use these filters. Model diagnostics remain a clearly labeled full-population benchmark.')
    st.divider();st.subheader('Analysis Context')
    st.write(f'**Snapshot:** {pd.Timestamp(m["as_of"]).strftime("%d %b %Y")}\n\n**Lookback:** {m["window_days"]} days\n\n**Currency:** GBP (£)\n\n**Fitted Clusters:** {m["selected_k"]}')
view=filter_audience(d,selected,baseline,country);summary=summarize_audience(view)
full_summary=summarize_audience(d)
actions=playbook.set_index('segment').to_dict('index')

st.caption('JOSEPH IKOGHO · DATA SCIENCE PORTFOLIO / 02')
st.title('RFM & Behavioral Customer Segmentation')
st.write('Understand the audience, choose a targeted campaign hypothesis, and export the customers to include.')
st.markdown(f'<div class="snapshot-band"><strong>Historical Analysis</strong> · Snapshot: <strong>{pd.Timestamp(m["as_of"]).strftime("%d %b %Y")}</strong> · {m["window_days"]}-Day Lookback · <strong>GBP (£)</strong></div>',unsafe_allow_html=True)
a,b,c,e=st.columns(4)
a.metric('Customers In Audience',f'{len(view):,}',delta=f'{len(view)/len(d):.1%} Of Dataset',delta_color='off')
b.metric('Segments In Audience',str(view.segment.nunique()),help=f'The model has {m["selected_k"]} fitted clusters. This count shows only segments present after filtering.')
c.metric('Historical Purchase Value',f'£{view.Monetary.sum():,.0f}',help='Positive purchase value within the window; excludes cancellations and returns. Not profit, net revenue or future lifetime value.')
e.metric('Median Days Since Purchase',f'{view.Recency.median():.0f} days' if len(view) else '—',help='Recency is measured at the historical snapshot, not today.')
st.caption(f'Selected Audience: {len(view):,} of {len(d):,} customers · {country}. Purchase value excludes returns/cancellations; no conversion uplift is claimed.')
page=st.radio('Workspace',PAGES,key='workspace',horizontal=True,label_visibility='collapsed')

def profile_table(frame,behavior=False):
    fields=['segment','customers','customer_share','value_share','Recency_median','Frequency_median','Monetary_median']
    if behavior:fields=['segment','average_order_value_median','unique_products_median','units_per_order_median','first_observed_age_days_median','repeat_buyer_share']
    display=humanize_frame(frame[fields],PROFILE_LABELS)
    formats={PROFILE_LABELS[c]:'{:.1%}' for c in ['customer_share','value_share','repeat_buyer_share'] if c in fields}
    formats.update({PROFILE_LABELS[c]:'£{:,.0f}' for c in ['Monetary_median','average_order_value_median'] if c in fields})
    formats.update({PROFILE_LABELS[c]:'{:,.0f}' for c in ['customers','Frequency_median','unique_products_median','units_per_order_median','first_observed_age_days_median'] if c in fields})
    if 'Recency_median' in fields:formats[PROFILE_LABELS['Recency_median']]='{:,.0f} days'
    st.dataframe(display.style.format(formats,na_rep='—'),hide_index=True,width='stretch',
        column_config={
            'Median Days Since Purchase':st.column_config.NumberColumn(help='Days since the latest eligible purchase at the snapshot. Lower is more recent.'),
            'Median Orders':st.column_config.NumberColumn(help='Median distinct-invoice count in the 365-day window; not line count or units.'),
            'Median Customer Purchase Value (£)':st.column_config.NumberColumn(help='Median positive purchase value per customer; not refund-adjusted net revenue.'),
            'Customer Share':st.column_config.NumberColumn(help='Customers in this segment / customers in the current audience.'),
            'Purchase-Value Share':st.column_config.NumberColumn(help='Segment purchase value / total purchase value of the current audience.'),
        })

def audience_table(frame):
    cols=['CustomerID','segment','baseline_tier','RFM_code','Recency','Frequency','Monetary','recommended_campaign','country']
    ui=humanize_frame(frame[cols],AUDIENCE_LABELS)
    st.dataframe(ui.style.format({'Historical Purchase Value (£)':'£{:,.0f}','Days Since Purchase':'{:,.0f}','Orders':'{:,.0f}'},na_rep='—'),hide_index=True,width='stretch')

if page=='Segment Overview':
    st.subheader('The Main Opportunity')
    if len(summary):
        lead=summary.sort_values('value_share',ascending=False).iloc[0]
        st.info(f'**{tc(lead.segment)}:** {int(lead.customers):,} customers ({lead.customer_share:.1%} of this audience) account for **{lead.value_share:.1%} of its historical purchase value**. **Campaign Hypothesis:** {actions[lead.segment]["message_or_offer"]}')
        st.subheader('Choose An Audience And A Campaign Hypothesis')
        columns=st.columns(len(summary))
        for col,row in zip(columns,summary.itertuples()):
            with col,st.container(border=True):
                st.markdown(f'<div class="segment-heading" style="border-color:{SEGMENT_COLORS[row.segment]}"><h3>{escape(tc(row.segment))}</h3></div>',unsafe_allow_html=True)
                st.write(f'**{int(row.customers):,} Customers** · {row.customer_share:.1%} of audience')
                st.write(f'**Purchase-Value Share:** {row.value_share:.1%}\n\n**Median Recency:** {row.Recency_median:.0f} days\n\n**Median Orders:** {row.Frequency_median:.0f}')
                action=actions[row.segment]
                st.markdown('**Campaign Hypothesis**');st.write(action['message_or_offer'])
                st.markdown('**Measure**');st.caption(action['primary_kpi'])
                st.button('View Audience',key='focus_'+row.segment,on_click=focus_segment,args=(row.segment,),width='stretch')
                subset=view[view.segment.eq(row.segment)]
                st.download_button('Export This Audience',subset.to_csv(index=False),'audience_'+row.segment.replace(' ','_')+'.csv','text/csv',key='card_export_'+row.segment,width='stretch')
        st.subheader('Compare Customer Share With Purchase-Value Share')
        st.altair_chart(share_chart(summary),width='stretch')
        st.altair_chart(count_chart(summary),width='stretch')
        st.subheader('Selected-Audience Profiles')
        profile_table(summary)
        with st.expander('Behavioral Details For The Selected Audience'):
            profile_table(summary,behavior=True)
            st.write('Order value, basket size, product breadth and first-observed age describe these groups. Only RFM enters K-Means. A top purchased SKU is not a validated interest profile.')
        st.subheader('Explore Purchase Patterns')
        x,y=st.columns([1,2])
        scale=x.radio('Purchase-Value Axis',['Logarithmic','Linear'],horizontal=True)
        zoom=y.checkbox('Zoom To The Lower 99% Of Purchase Values',help='Display-only crop within the selected audience. It changes neither the model nor KPIs, tables or exports.')
        plotted,cutoff,hidden=scatter_audience(view,zoom)
        if zoom:st.caption(f'{hidden:,} customers above £{cutoff:,.0f} are hidden in this chart only. All {len(view):,} selected customers remain in the metrics and exports.')
        else:st.caption('All selected customers are plotted. Hover for customer ID, segment, recency, orders and purchase value. Point size represents order frequency.')
        st.altair_chart(scatter_chart(plotted,scale=='Logarithmic'),width='stretch')
    else:st.info('No customers match these filters. Use Select All or Reset to restore the audience.')
    with st.expander('Full-Population Benchmark — Unaffected By Audience Filters'):
        st.caption(f'All {len(d):,} modeled customers at the frozen historical snapshot. The main overview above uses only the selected audience.')
        profile_table(full_summary)
    with st.expander('Data Definitions And Interpretation Limits'):
        st.write('Purchase value is not net revenue, profit or future lifetime value. Wholesalers are present, so large baskets need not reflect household wealth. Household, demographic, browsing, marketing-permission and campaign-outcome fields are unavailable. Historical grouping does not demonstrate conversion uplift.')

elif page=='Manual RFM Baseline':
    st.subheader('RFM Calculated Manually In Pandas')
    st.write('Recency = days since last eligible purchase; Frequency = distinct invoices in the 365-day window; Monetary = positive quantity × price in GBP. Lower Recency is better; higher Frequency and Monetary are better.')
    st.write('Each metric gets a tied-score-safe 1–5 quintile score. Ordered rules create the manual tiers before K-Means is fitted. Newly observed is relative to the window, not first-ever membership.')
    st.subheader('Manual Tiers In The Selected Audience')
    counts=view.baseline_tier.map(tc).value_counts().rename_axis('Manual RFM Tier').reset_index(name='Customers')
    st.dataframe(counts,hide_index=True,width='stretch')
    st.subheader('Manual Tiers Compared With Named Clusters')
    cross=pd.crosstab(view.baseline_tier.map(tc),view.segment.map(tc));cross.index.name='Manual RFM Tier';cross.columns.name='Customer Segment'
    st.dataframe(cross,width='stretch')
    st.caption('Both tables reflect the selected audience. Neither method is ground truth; disagreement is diagnostic, not classification error.')
    with st.expander('Full-Source Cleaning Audit — Unaffected By Audience Filters'):
        audit=pd.read_csv(ROOT/'outputs/cleaning_audit.csv').rename(columns={'step':'Cleaning Step','remaining':'Remaining Rows','removed':'Removed Rows'})
        audit['Cleaning Step']=audit['Cleaning Step'].map(tc)
        st.dataframe(audit,hide_index=True,width='stretch')

elif page=='Campaign Playbook':
    st.subheader('Targeted Campaign Hypotheses For The Selected Audience')
    for row in playbook[playbook.segment.isin(view.segment.unique())].to_dict('records'):
        count=int(view.segment.eq(row['segment']).sum())
        with st.expander(f'{tc(row["segment"])} · {count:,} Customers · {tc(row["campaign"])}'):
            st.write(row['message_or_offer']);st.markdown('**Primary KPI:** '+row['primary_kpi']);st.caption(row['guardrail'])
    if view.empty:st.info('Select an audience to view its campaign hypotheses.')
    st.info('Manual overlays remain visible in Recommended Campaign: high-value-at-risk tiers receive a win-back hypothesis; newly observed tiers receive second-purchase onboarding. Broad cluster medians must not hide valuable exceptions.')
    st.download_button('Download Campaign Playbook',playbook[playbook.segment.isin(view.segment.unique())].to_csv(index=False),'campaign_playbook.csv','text/csv')
    st.subheader('Plan An Experiment Before Claiming Uplift')
    st.write('Randomize eligible, consented customers within each segment to targeted treatment or control. Prespecify horizon, contribution metric, costs, baseline conversion, minimum detectable effect and sample size. Account for multiple segment tests and record treatment exposure and redemption.')
    contact=st.number_input('Planning Cost Per Contacted Customer (£)',0.,100.,.20,.05)
    st.metric('Selected-Audience Contact Budget',f'£{len(view)*contact:,.2f}')
    st.caption('Planning cost only; no observed treatment effects, consent, margins or campaign outcomes are present.')
    st.subheader('What Broader Data Could Add')
    st.write('Authorized product taxonomy, opt-in browsing/engagement, household composition or lifecycle lenses could add context. Validate consent, usefulness and fairness; do not infer household composition or personal interests from purchases alone.')

elif page=='Audience Export':
    st.subheader('Review And Export The Selected Audience')
    audience_table(view)
    st.download_button('Download Selected Audience',view.to_csv(index=False),'segmented_audience.csv','text/csv')
    st.caption('Downloads preserve the documented original CSV field names for reproducible analysis. Public pseudonymous IDs are not a production contact list; real activation requires identity resolution and contact permissions.')
    with st.expander('Behavioral Fields In The Export'):
        fields=['CustomerID','average_order_value','unique_products','first_observed_age_days','country','top_product_code']
        details=humanize_frame(view[fields],AUDIENCE_LABELS)
        st.dataframe(details.style.format({'Average Order Value (£)':'£{:,.0f}','Product Breadth':'{:,.0f}','Days Since First Observed Purchase':'{:,.0f} days'},na_rep='—'),hide_index=True,width='stretch')

elif page=='Cluster Evidence':
    st.subheader('Elbow Evidence And Robustness')
    st.info(f'Model Diagnostics: all {len(d):,} modeled customers. Audience filters do not refit K-Means, change k or recalculate this evidence.')
    import altair as alt
    elbow=pd.read_csv(ROOT/'outputs/elbow_diagnostics.csv')
    chart=alt.Chart(elbow).mark_line(point=True,color='#087F83').encode(x=alt.X('k:O',title='Number Of Clusters'),y=alt.Y('inertia:Q',title='Within-Cluster Sum Of Squares'),tooltip=[alt.Tooltip('k:O',title='Clusters'),alt.Tooltip('inertia:Q',title='Inertia',format=',.0f')]).properties(height=300,title='Elbow Curve')
    st.altair_chart(chart,width='stretch')
    st.dataframe(elbow.rename(columns={'k':'Clusters','inertia':'Inertia','silhouette_sampled':'Sampled Silhouette','chord_distance':'Normalized Chord Distance'}),hide_index=True,width='stretch')
    st.write(f'The normalized endpoint-chord gap over k=1…10 selects k={m["selected_k"]}; range 1…8 also selects k={m["elbow_k_range_1_to_8"]}. This heuristic supports a practical candidate, not a unique natural taxonomy. Silhouette favors two more strongly; three creates a finer middle group.')
    st.write(f'Chosen-k sampled silhouette: {m["silhouette_sampled"]:.3f}. Minimum repeated-seed ARI: {m["seed_ari_min"]:.3f}. Main versus 99%-capped RFM ARI: {m["capped_99pct_ari"]:.3f}. These are internal diagnostics, not accuracy or campaign outcomes.')
    st.image(str(ROOT/'outputs/segmentation_evidence.png'))
    st.caption('Only scaled log-RFM enters K-Means. No main-model winsorization. PCA can hide three-dimensional overlap.')

elif page=='Assign An RFM CSV':
    st.subheader('Assign Comparable RFM To Frozen Segments')
    st.write('Upload CustomerID, Recency (days), Frequency (distinct invoices), Monetary (GBP), calculated using the same 365-day definitions. This does not retrain the model. A new period or business requires validation.')
    st.download_button('Download Example RFM',(ROOT/'data/example_rfm.csv').read_bytes(),'example_rfm.csv','text/csv')
    upload=st.file_uploader('Customer RFM CSV',type='csv')
    if upload is not None:
        try:
            result=assign_segments(pd.read_csv(upload,dtype={'CustomerID':'string'}))
            assigned=humanize_frame(result,AUDIENCE_LABELS)
            assigned_formats={c:fmt for c,fmt in {'Historical Purchase Value (£)':'£{:,.0f}','Days Since Purchase':'{:,.0f} days','Orders':'{:,.0f}','Distance To Cluster Center':'{:.2f}'}.items() if c in assigned}
            st.dataframe(assigned.style.format(assigned_formats,na_rep='—'),hide_index=True,width='stretch')
            st.download_button('Download Assignments',result.to_csv(index=False),'assigned_segments.csv','text/csv')
            st.caption('A newly observed baseline tier requires first_observed_age_days; distance to center is not confidence or probability.')
        except (ValueError,TypeError,KeyError) as exc:st.error(str(exc))
st.divider();st.caption('Designed By Nova Agentic · Portfolio By Joseph Ikogho · UCI Online Retail · No Campaigns Sent')
