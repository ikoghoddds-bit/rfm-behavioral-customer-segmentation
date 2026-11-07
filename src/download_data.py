"""Download the original UCI workbook and preserve all rows as compressed CSV."""
from pathlib import Path
from urllib.request import urlopen
import zipfile,io,json,hashlib
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
URL='https://archive.ics.uci.edu/static/public/352/online+retail.zip'

def convert(payload):
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        name=next(n for n in z.namelist() if n.endswith('.xlsx'))
        workbook=z.read(name)
    d=pd.read_excel(io.BytesIO(workbook),engine='openpyxl')
    root=ROOT/'data';root.mkdir(exist_ok=True)
    path=root/'online_retail.csv.gz'
    # Preserve missing IDs, negatives and cancellations for transparent cleaning.
    d.to_csv(path,index=False,compression={'method':'gzip','mtime':0})
    (root/'source.json').write_text(json.dumps({'source_url':URL,'dataset_url':'https://archive.ics.uci.edu/dataset/352/online+retail',
        'citation':'Chen, D. (2015). Online Retail. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33',
        'license':'CC BY 4.0','source_rows':len(d),'source_workbook_sha256':hashlib.sha256(workbook).hexdigest(),
        'csv_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'modification':'Workbook serialized as gzip CSV; no rows removed at conversion.'},indent=2))
    print(f'Converted {len(d):,} original transaction lines.')

if __name__=='__main__':
    with urlopen(URL,timeout=120) as response:convert(response.read())
