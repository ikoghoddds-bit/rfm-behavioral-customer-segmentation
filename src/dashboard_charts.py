"""Consistent segment colors, readable axes and labels for the local dashboard."""
import altair as alt
from src.presentation import SEGMENT_ORDER,SEGMENT_COLORS,title_case

ORDER=[title_case(s) for s in SEGMENT_ORDER]
COLORS=[SEGMENT_COLORS[s] for s in SEGMENT_ORDER]

def finish(chart):
    return chart.configure_axis(labelFontSize=13,titleFontSize=14).configure_legend(labelFontSize=13,titleFontSize=14,labelLimit=500).configure_title(fontSize=17,anchor='start')

def count_chart(summary):
    d=summary[['segment','customers']].copy()
    d['Customer Segment']=d.segment.map(title_case)
    d=d.rename(columns={'customers':'Customers'})
    base=alt.Chart(d).encode(
        y=alt.Y('Customer Segment:N',sort=ORDER,title=None,axis=alt.Axis(labelLimit=400)),
        x=alt.X('Customers:Q',title='Customers',scale=alt.Scale(domain=[0,float(d.Customers.max())*1.2])),
        tooltip=[alt.Tooltip('Customer Segment:N'),alt.Tooltip('Customers:Q',format=',.0f')],
    )
    bars=base.mark_bar(size=30,cornerRadiusEnd=4).encode(color=alt.Color('Customer Segment:N',scale=alt.Scale(domain=ORDER,range=COLORS),legend=None))
    labels=base.mark_text(align='left',dx=7,fontSize=14).encode(text=alt.Text('Customers:Q',format=',.0f'))
    return finish((bars+labels).properties(height=230,title='Customers Per Segment'))

def share_chart(summary):
    d=summary[['segment','customer_share','value_share']].rename(columns={'customer_share':'Customer Share','value_share':'Purchase-Value Share'}).copy()
    d['Customer Segment']=d.segment.map(title_case)
    base=alt.Chart(d).transform_fold(['Customer Share','Purchase-Value Share'],as_=['Share Type','Share']).encode(
        y=alt.Y('Customer Segment:N',sort=ORDER,title=None,axis=alt.Axis(labelLimit=400)),
        yOffset=alt.YOffset('Share Type:N',sort=['Customer Share','Purchase-Value Share']),
        x=alt.X('Share:Q',title='Share Of Selected Audience',scale=alt.Scale(domain=[0,1.07]),axis=alt.Axis(format='.0%',values=[0,.25,.5,.75,1])),
        opacity=alt.Opacity('Share Type:N',scale=alt.Scale(domain=['Customer Share','Purchase-Value Share'],range=[.45,1]),legend=alt.Legend(title='Share Type',orient='bottom')),
        tooltip=[alt.Tooltip('Customer Segment:N'),alt.Tooltip('Share Type:N'),alt.Tooltip('Share:Q',format='.1%')],
    )
    labels=base.mark_text(align='left',dx=6,fontSize=13).encode(text=alt.Text('Share:Q',format='.1%'),opacity=alt.value(1))
    return finish((base.mark_bar(cornerRadiusEnd=3).encode(color=alt.Color('Customer Segment:N',scale=alt.Scale(domain=ORDER,range=COLORS),legend=None))+labels).properties(height=280,title='Customer Share Vs Purchase-Value Share'))

def scatter_chart(view,log_scale=True):
    d=view.copy();d['Customer Segment']=d.segment.map(title_case)
    chart=alt.Chart(d).mark_circle(opacity=.65,strokeWidth=.3).encode(
        x=alt.X('Recency:Q',title='Days Since Last Purchase'),
        y=alt.Y('Monetary:Q',title='Historical Purchase Value (£)',scale=alt.Scale(type='log',zero=False) if log_scale else alt.Scale(zero=True),axis=alt.Axis(format=',.0f')),
        color=alt.Color('Customer Segment:N',scale=alt.Scale(domain=ORDER,range=COLORS),legend=alt.Legend(title='Customer Segment',orient='bottom',columns=1)),
        size=alt.Size('Frequency:Q',scale=alt.Scale(type='sqrt',range=[25,230]),legend=None),
        tooltip=[alt.Tooltip('CustomerID:N',title='Customer ID'),alt.Tooltip('Customer Segment:N'),
                 alt.Tooltip('Recency:Q',title='Days Since Purchase',format=',.0f'),
                 alt.Tooltip('Frequency:Q',title='Orders',format=',.0f'),
                 alt.Tooltip('Monetary:Q',title='Purchase Value (£)',format=',.2f'),
                 alt.Tooltip('average_order_value:Q',title='Average Order Value (£)',format=',.2f')],
    ).interactive().properties(height=400,title='Recency And Purchase Value By Segment')
    return finish(chart)
