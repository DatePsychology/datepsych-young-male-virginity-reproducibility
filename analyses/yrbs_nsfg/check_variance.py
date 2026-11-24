#!/usr/bin/env python3
"""Sanity-check independent design SE against stratified with-replacement PSU bootstrap."""
import numpy as np, pandas as pd
from inspect_input import load
from replicate_yrbs import ratio
from pathlib import Path
rng=np.random.default_rng(20261123);R=2000;out=[]
for year in [2011,2019,2021,2023,2025]:
 d,_=load(year)
 d['sexever']=np.where(d.everraw.isin([1,2]),d.everraw.eq(1).astype(float),np.nan)
 domain=d.sexcode.eq(2)&d.sexever.notna();r=ratio(d,d.sexcode.eq(2))
 d['w_num']=np.where(domain,d.sexever.fillna(0)*d.weight,0.)
 d['w_den']=np.where(domain,d.weight,0.)
 c=d.groupby(['stratum','psu'])[['w_num','w_den']].sum()
 by=[z[['w_num','w_den']].to_numpy() for _,z in c.groupby(level=0)]
 boot=[]
 for b in range(R):
  n=0.;v=0.
  for a in by:
   m=len(a);ix=rng.integers(m,size=m-1)
   sums=(m/(m-1))*a[ix].sum(axis=0); n+=sums[0];v+=sums[1]
  boot.append(n/v)
 bs=np.std(boot,ddof=1)
 out.append(dict(year=year,linear_SE_pp=r['se']*100,psu_bootstrap_SE_pp=bs*100,ratio=bs/r['se'],bootstrap_95_low_pp=100*np.quantile(boot,.025),bootstrap_95_hi_pp=100*np.quantile(boot,.975)))
 print(out[-1])
pd.DataFrame(out).to_csv(Path(__file__).parent/'output'/'independent_bootstrap_variance_check.csv',index=False)
