"""python -m src.segment — descriptive, reproducible RFM clustering."""
from pathlib import Path
import json,hashlib,importlib.metadata,platform,textwrap
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer,StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score,adjusted_rand_score
from src.features import clean_transactions,compute_rfm,fit_baseline,RFM
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs';SEED=42

def elbow_k(ks,inertias):
    """Largest perpendicular distance below the normalized endpoint chord.

    An explicit elbow heuristic, not a proof of uniquely true natural segments.
    The endpoint range affects the result; sensitivity and silhouettes accompany it.
    """
    x=np.asarray(ks,dtype=float);y=np.asarray(inertias,dtype=float)
    if len(x)<3 or y[0]<=y[-1]:raise ValueError('Elbow needs at least three decreasing inertia values.')
    xn=(x-x[0])/(x[-1]-x[0]);yn=(y-y[-1])/(y[0]-y[-1])
    distances=(1-xn-yn)/np.sqrt(2)
    index=int(np.argmax(distances[1:-1]))+1
    return int(x[index]),distances

def name_segments(profiles,customers):
    names={};used=set()
    for cid,p in profiles.sort_values('Monetary_median',ascending=False).iterrows():
        recent=p.Recency_median<=60;lapsed=p.Recency_median>120
        valuable=p.Monetary_median>=customers.Monetary.quantile(.65)
        repeat=p.Frequency_median>=3
        if valuable and lapsed:base='High value at risk of lapsing'
        elif valuable and recent and repeat:base='Loyal high-value customers'
        elif recent and p.first_observed_age_days_median<=60 and p.Frequency_median<=2:base='Newly observed customers still exploring'
        elif recent:base='Active developing customers'
        elif lapsed:base='Lapsed occasional customers'
        elif repeat:base='Repeat customers needing re-engagement'
        else:base='Occasional customers cooling off'
        # Only if two profiles meet the same broad rule, distinguish them by
        # actual median RFM traits, never expose arbitrary cluster IDs as names.
        name=base
        if name in used:name=base+' — higher historical spend' if valuable else base+' — lower historical spend'
        if name in used:name=base+f' — typically {int(p.Frequency_median)} orders, {int(p.Recency_median)} days inactive'
        names[int(cid)]=name;used.add(name)
    return names

def playbook(name):
    if 'risk of lapsing' in name:return ('Personalized win-back','Acknowledge purchase history; offer relevant replenishment or service support.','Incremental reactivation and contribution','Avoid blanket deep discounts; prior spend is not future value.')
    if 'Loyal' in name:return ('VIP recognition and cross-sell','Early access or relevant bundles; test non-discount benefits first.','Incremental contribution per eligible customer','Do not subsidize purchases that would occur anyway.')
    if 'New' in name:return ('Second-purchase onboarding','Helpful product guidance and a time-limited second-order test.','Second-purchase rate within 30 days','First observed does not prove first-ever customer.')
    if 'Recent' in name or 'Active' in name:return ('Nurture repeat purchasing','Relevant product follow-up; use observed basket history cautiously.','Incremental 30-day repeat-purchase rate','Interest is not inferred beyond observed purchases.')
    if 'Lapsed' in name:return ('Low-cost reactivation pilot','Test a small email group and suppress nonresponders after the test.','Incremental reactivation net of contact cost','Do not spend heavily on low-response customers without evidence.')
    return ('Re-engagement and relevance','Test reminders and basket-adjacent products with a holdout.','Incremental repeat-purchase contribution','Optimize profit rather than clicks or open rate alone.')

def main():
    OUT.mkdir(exist_ok=True)
    raw=pd.read_csv(ROOT/'data/online_retail.csv.gz',dtype={'InvoiceNo':'string','StockCode':'string'})
    clean,audit,as_of=clean_transactions(raw);audit.to_csv(OUT/'cleaning_audit.csv',index=False)
    rfm=compute_rfm(clean,as_of);customers,cuts=fit_baseline(rfm)
    prep=Pipeline([('log',FunctionTransformer(np.log1p,validate=True)),('scale',StandardScaler())])
    z=prep.fit_transform(customers[RFM])
    ks=list(range(1,11));rows=[];models={}
    for k in ks:
        model=KMeans(n_clusters=k,n_init=20,random_state=SEED).fit(z);models[k]=model
        sil=float(silhouette_score(z,model.labels_,sample_size=min(2000,len(z)),random_state=SEED)) if k>1 else None
        rows.append({'k':k,'inertia':model.inertia_,'silhouette_sampled':sil})
    elbow=pd.DataFrame(rows);chosen,dist=elbow_k(ks,elbow.inertia);elbow['chord_distance']=dist
    elbow.to_csv(OUT/'elbow_diagnostics.csv',index=False)
    model=models[chosen];customers['cluster_id']=model.labels_
    # Profile original units, not scaled coordinates; nontechnical readers need
    # days, invoice counts and GBP to understand the groups.
    aggregate={c:['median','mean'] for c in RFM+['first_observed_age_days','average_order_value','unique_products','units_per_order']}
    profiles=customers.groupby('cluster_id').agg(aggregate);profiles.columns=['_'.join(x) for x in profiles.columns]
    names=name_segments(profiles,customers);customers['segment']=customers.cluster_id.map(names)
    profiles['segment']=[names[int(c)] for c in profiles.index]
    profiles['customers']=customers.groupby('cluster_id').size()
    profiles['gross_purchase_value']=customers.groupby('cluster_id').Monetary.sum()
    profiles['customer_share']=profiles.customers/len(customers)
    profiles['value_share']=profiles.gross_purchase_value/customers.Monetary.sum()
    profiles['repeat_buyer_share']=customers.groupby('cluster_id').repeat_buyer.mean()
    profiles['dominant_country']=customers.groupby('cluster_id').country.agg(lambda x:x.mode().iloc[0])
    actions=[]
    for c,p in profiles.iterrows():
        campaign,message,kpi,caution=playbook(p.segment)
        actions.append({'segment':p.segment,'customers':int(p.customers),'campaign':campaign,'message_or_offer':message,'primary_kpi':kpi,'guardrail':caution})
    pd.DataFrame(actions).to_csv(OUT/'campaign_playbook.csv',index=False)
    # Preserve high-risk and newly observed manual tiers as activation overlays.
    # A broad cluster's median can otherwise hide valuable exceptions.
    customers['recommended_campaign']=customers.segment.map({name:playbook(name)[0] for name in names.values()})
    customers.loc[customers.baseline_tier.eq('High value at risk of lapsing'),'recommended_campaign']='Personalized win-back (RFM overlay)'
    customers.loc[customers.baseline_tier.str.startswith('New'),'recommended_campaign']='Second-purchase onboarding (RFM overlay)'
    customers.to_csv(OUT/'customer_segments.csv',index=False)
    profiles.reset_index().to_csv(OUT/'segment_profiles.csv',index=False)
    pd.crosstab(customers.baseline_tier,customers.segment).to_csv(OUT/'baseline_vs_clusters.csv')
    pd.crosstab(customers.baseline_tier,columns='customers').to_csv(OUT/'baseline_counts.csv')
    # Repeated seeds evaluate optimization sensitivity at the chosen k.
    stability=[]
    for seed in [0,7,21,99,2026]:
        other=KMeans(n_clusters=chosen,n_init=20,random_state=seed).fit(z)
        stability.append({'seed':seed,'adjusted_rand_index':adjusted_rand_score(model.labels_,other.labels_)})
    pd.DataFrame(stability).to_csv(OUT/'seed_stability.csv',index=False)
    # A 99th-percentile cap is diagnostic only; the main model retains outliers.
    capped=customers[RFM].clip(upper=customers[RFM].quantile(.99),axis=1)
    zc=Pipeline([('log',FunctionTransformer(np.log1p,validate=True)),('scale',StandardScaler())]).fit_transform(capped)
    sensitivity_model=KMeans(n_clusters=chosen,n_init=20,random_state=SEED).fit(zc)
    cap_ari=adjusted_rand_score(model.labels_,sensitivity_model.labels_)
    range_k,_=elbow_k(ks[:8],elbow.inertia.iloc[:8])
    bundle={'prep':prep,'model':model,'segment_names':names,'baseline_cutoffs':cuts,'features':RFM,'as_of':str(as_of.date()),'window_days':365}
    joblib.dump(bundle,OUT/'model.joblib')
    # Persist a target-free RFM upload example, not a set of invented customers.
    customers[['CustomerID']+RFM].head(20).to_csv(ROOT/'data/example_rfm.csv',index=False)
    metrics={'raw_rows':len(raw),'eligible_lines':len(clean),'customers':len(customers),'orders':int(clean.groupby('CustomerID').InvoiceNo.nunique().sum()),
        'as_of':str(as_of.date()),'window_start':str((as_of-pd.Timedelta(days=365)).date()),'window_days':365,'selected_k':chosen,
        'silhouette_sampled':float(elbow.loc[elbow.k==chosen,'silhouette_sampled'].iloc[0]),
        'gross_purchase_value_gbp':float(customers.Monetary.sum()),'seed_ari_min':float(pd.DataFrame(stability).adjusted_rand_index.min()),
        'capped_99pct_ari':float(cap_ari),'elbow_k_range_1_to_8':range_k,'baseline_tiers':int(customers.baseline_tier.nunique()),
        'baseline_cutoffs':cuts,'data_sha256':hashlib.sha256((ROOT/'data/online_retail.csv.gz').read_bytes()).hexdigest()}
    (OUT/'metrics.json').write_text(json.dumps(metrics,indent=2))
    plt.rcParams.update({'axes.spines.top':False,'axes.spines.right':False,'font.size':10})
    fig,ax=plt.subplots(2,3,figsize=(17,10),layout='constrained')
    ax[0,0].plot(elbow.k,elbow.inertia,'o-',color='#087e8b');ax[0,0].axvline(chosen,ls='--',color='#b86b05');ax[0,0].set(title=f'Elbow curve: candidate k={chosen}',xlabel='k',ylabel='Within-cluster sum of squares')
    ax[0,1].plot(elbow.k.iloc[1:],elbow.silhouette_sampled.iloc[1:],'o-',color='#087e8b');ax[0,1].set(title='Sampled silhouette: supporting evidence',xlabel='k',ylabel='Silhouette')
    pca=PCA(n_components=2,random_state=SEED);coords=pca.fit_transform(z)
    for c in range(chosen):
        mask=customers.cluster_id==c;ax[0,2].scatter(coords[mask,0],coords[mask,1],s=6,alpha=.45,label=names[c])
    ax[0,2].set(title='PCA view of scaled log-RFM',xlabel='PC1',ylabel='PC2')
    ax[0,2].legend(fontsize=7,loc='upper left',markerscale=2)
    # Plot axes use plain-English names; PCA colors are exploration, not the
    # output naming scheme. 2D projections can hide overlap in three dimensions.
    profiles.set_index('segment').customers.sort_values().plot.barh(ax=ax[1,0],color='#087e8b');ax[1,0].set(title='Customers per named segment',ylabel='')
    profiles.set_index('segment').value_share.sort_values().plot.barh(ax=ax[1,1],color='#b86b05');ax[1,1].set(title='Share of historical purchase value',ylabel='')
    for axis in [ax[1,0],ax[1,1]]:
        axis.set_yticks(axis.get_yticks(),[textwrap.fill(t.get_text(),22) for t in axis.get_yticklabels()])
    med=profiles.set_index('segment')[[c+'_median' for c in RFM]];normalized=(med-med.min())/(med.max()-med.min()).replace(0,1)
    ax[1,2].imshow(normalized,aspect='auto',cmap='YlGnBu',vmin=0,vmax=1);ax[1,2].set(xticks=range(3),xticklabels=RFM,yticks=range(chosen),yticklabels=[textwrap.fill(t,22) for t in med.index],title='Median profiles in original units')
    for i in range(chosen):
        for j in range(3):ax[1,2].text(j,i,f'{med.iloc[i,j]:,.0f}',ha='center',va='center',color='white' if normalized.iloc[i,j]>.55 else '#172b3a',fontsize=9)
    fig.savefig(OUT/'segmentation_evidence.png',dpi=150);plt.close(fig)
    (OUT/'environment.json').write_text(json.dumps({'python':platform.python_version(),'packages':{p:importlib.metadata.version(p) for p in ['numpy','pandas','scikit-learn','scipy','matplotlib','joblib','streamlit','openpyxl','pytest','nbformat']}},indent=2))
    print(json.dumps(metrics,indent=2));return metrics

if __name__=='__main__':main()
