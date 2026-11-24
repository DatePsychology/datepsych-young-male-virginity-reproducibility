#!/usr/bin/env python3
"""NSFG comparison (separate target populations/constructs). Supply NSFG_DIR with public data."""
import os,re,glob,zipfile,io
from pathlib import Path
import numpy as np,pandas as pd
from replicate_yrbs import ratio
ROOT=Path(__file__).resolve().parent
IN=Path(os.environ.get('NSFG_DIR',str(ROOT.parent)))
OUT=ROOT/'output';OUT.mkdir(exist_ok=True)

def fwf_fields(fname,cols):
 text=Path(fname).read_text(encoding='latin1')
 pat=re.compile(r'_column\s*\(\s*(\d+)\s*\)\s+(\w+)\s+(\w+)\s+(%\d+[A-Za-z])',re.I)
 f={v.upper(): (int(a),c,fmt) for a,c,v,fmt in pat.findall(text)}
 assert all(c in f for c in cols),(fname,set(cols)-set(f))
 return [(f[c][0]-1,f[c][0]-1+int(re.search(r'(\d+)',f[c][2])[1])) for c in cols]

def get_old(y):
 dct=glob.glob(str(IN/f'{y}_MaleSetup*.dct'));assert len(dct)==1,(y,dct)
 fields=['AGER','HADSEX',f'WGT{y}','SEST','SECU']
 df=pd.read_fwf(IN/f'{y}_MaleData.dat',colspecs=fwf_fields(dct[0],fields),names=fields,dtype='str')
 for c in fields:df[c]=pd.to_numeric(df[c],errors='coerce')
 df=df.rename(columns={'AGER':'age','HADSEX':'hadsex',f'WGT{y}':'weight','SEST':'stratum','SECU':'psu'})
 return df

def get_new():
 p=IN/'NSFG-2022-2023-MaleRespPUFData.zip'
 with zipfile.ZipFile(p) as f:
  names=[n for n in f.namelist() if n.lower().endswith('.csv')];assert len(names)==1,names
  df=pd.read_csv(io.BytesIO(f.read(names[0])),usecols=['AGER','HADSEX','WGT2022_2023','VEST','VECL'])
 return df.rename(columns={'AGER':'age','HADSEX':'hadsex','WGT2022_2023':'weight','VEST':'stratum','VECL':'psu'})

if __name__=='__main__':
 out=[]
 for y in ['2011_2013','2013_2015','2015_2017','2017_2019','2022_2023']:
  d=get_old(y) if y!='2022_2023' else get_new()
  d['sexever']=np.where(d.hadsex.isin([1,2]),d.hadsex.eq(1).astype(float),np.nan)
  for ages in [(15,17),(15,19),(18,19)]:
   # Note: NSFG counts men who have ever had heterosexual vaginal intercourse, unlike YRBS broader intercourse wording
   r=ratio(d,d.age.between(*ages));out.append({'wave':y,'age_group':f'{ages[0]}-{ages[1]}','sexever_vaginal_female':r['p']*100,'CI_low':r['lo']*100,'CI_high':r['hi']*100,'n':r['n'],'se_pp':r['se']*100})
  print(y,'n',len(d),'15-17',round(out[-3]['sexever_vaginal_female'],2))
 pd.DataFrame(out).to_csv(OUT/'nsfg_age_15_19_comparator.csv',index=False,float_format='%.6f')
