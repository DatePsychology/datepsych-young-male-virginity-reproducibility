#!/usr/bin/env python3
"""Sensitivity to item nonresponse: weighted main-effects age+grade prediction plus MNAR odds multipliers. Not nonparticipation adjustment."""
import numpy as np,pandas as pd
from scipy.special import expit,logit
import statsmodels.api as sm
from inspect_input import load,files
from pathlib import Path
ROOT=Path(__file__).resolve().parent
results=[]
for year in files:
 d,_=load(year);d=d[d.sexcode==2].copy();d=d[d.weight.gt(0)].copy()
 d['ever']=np.where(d.everraw.isin([1,2]),d.everraw.eq(1).astype(float),np.nan)
 d['agec']=d.agecode.fillna(-9).clip(lower=3).astype(int).astype(str)
 d['gradec']=d.gradecode.fillna(-9).astype(int).astype(str)
 X=pd.get_dummies(d[['agec','gradec']],drop_first=True,dtype=float)
 X=sm.add_constant(X,has_constant='add')
 obs=d.ever.notna()
 # pseudo sample weights only affect point model fit, not inferential SE here
 w=d.weight/d.weight[obs].mean()
 fit=sm.GLM(d.loc[obs,'ever'],X.loc[obs],family=sm.families.Binomial(),freq_weights=w[obs]).fit(maxiter=150)
 pred=fit.predict(X)
 d['phat']=pred
 valid_w=d.loc[obs,'weight'].sum(); missing_w=d.loc[~obs,'weight'].sum(); denom=valid_w+missing_w
 event_w=(d.loc[obs,'ever']*d.loc[obs,'weight']).sum()
 rec={'year':year,'n_male':len(d),'n_missing':int((~obs).sum()),'weighted_missing_fraction':missing_w/denom,'observed_rate':event_w/valid_w,'age_grade_MAR':(event_w+(d.loc[~obs,'weight']*pred[~obs]).sum())/denom}
 for OR in [0.25,0.5,1,2,4]:
  q=OR*pred/(1-pred+OR*pred)
  rec['MNAR_OR_'+str(OR)]=(event_w+(d.loc[~obs,'weight']*q[~obs]).sum())/denom
 results.append(rec)
 print(year,'MAR',round(rec['age_grade_MAR']*100,2),'MNAR0.5',round(rec['MNAR_OR_0.5']*100,2),'MNAR2',round(rec['MNAR_OR_2']*100,2))
pd.DataFrame(results).to_csv(ROOT/'output'/'yrbs_missingness_age_grade_MNAR.csv',index=False,float_format='%.7f')
