"""python -m src.predict input_rfm.csv output_segments.csv"""
from pathlib import Path
import sys
import pandas as pd
import joblib
from src.features import validate_rfm,apply_baseline,RFM
ROOT=Path(__file__).resolve().parents[1]

def assign_segments(frame):
    d=validate_rfm(frame);bundle=joblib.load(ROOT/'outputs/model.joblib') # Trusted artifact only.
    z=bundle['prep'].transform(d[RFM]);labels=bundle['model'].predict(z)
    d['segment']=pd.Series(labels,index=d.index).map(bundle['segment_names'])
    d['cluster_id']=labels
    d['distance_to_center']=bundle['model'].transform(z).min(axis=1)
    # Missing first-observed history cannot justify calling someone "new".
    scored=apply_baseline(d,bundle['baseline_cutoffs'])
    return scored

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('Usage: python -m src.predict input_rfm.csv output_segments.csv')
    assign_segments(pd.read_csv(sys.argv[1],dtype={'CustomerID':'string'})).to_csv(sys.argv[2],index=False)
