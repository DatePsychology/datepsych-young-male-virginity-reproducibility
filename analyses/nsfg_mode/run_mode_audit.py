#!/usr/bin/env python3
"""NSFG 2017-19 and 2022-23 mode/comparability audit. Public-use respondent data required.
Rao-Wu-type within-stratum PSU rescaled bootstrap; no causal claims from mode.
"""
import io, zipfile, re, json, warnings, math, os
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.api as sm
from scipy.special import expit
HERE=Path(__file__).resolve().parent
BASE=Path(os.environ.get('NSFG_DATA_ROOT', HERE/'input'))
OUT=HERE/'output';OUT.mkdir(exist_ok=True)
SEED=20261123; N_BOOT=400

def field_spec(dct,need):
 t=Path(dct).read_text(encoding='latin1');pat=re.compile(r'_column\s*\(\s*(\d+)\s*\)\s+(\w+)\s+(\w+)\s+(%[0-9]+[A-Za-z])',re.I)
 f={n.upper():(int(start),str(fmt)) for start,typ,n,fmt in pat.findall(t)}
 assert set(need).issubset(f),set(need)-set(f)
 return [(f[c][0]-1,f[c][0]-1+int(re.search(r'(\d+)',f[c][1])[1])) for c in need]

def build():
 cols=['AGER','HADSEX','HIEDUC','HISPRACE2','ORIENT_A','ORIENT_B','WGT2017_2019','SEST','SECU','RMARITAL','POVERTY']
 old=pd.read_fwf(BASE/'2017_2019_MaleData.dat',colspecs=field_spec(next(iter(sorted(BASE.glob('2017_2019_MaleSetup*.dct')))),cols),names=cols,dtype='str').apply(pd.to_numeric,errors='coerce')
 old['wave']=0;old['mode']=0;old['straight']=old.ORIENT_A.eq(1)|old.ORIENT_B.eq(2)
 old['w']=old.WGT2017_2019;old['strat']=old.SEST;old['psu']=old.SECU
 old['education']=pd.cut(old.HIEDUC,bins=[0,8,9,11,15],labels=['below_hs','hs','some_college','ba_plus'])
 zipf=zipfile.ZipFile(BASE/'NSFG-2022-2023-MaleRespPUFData.zip');new=pd.read_csv(io.BytesIO(zipf.read('NSFG_2022_2023_MaleRespPUFData.csv')),low_memory=False)
 new['wave']=1;new['mode']=new.FTFMODE;new['straight']=new.ORIENT.eq(2)
 new['w']=new.WGT2022_2023;new['strat']=new.VEST;new['psu']=new.VECL
 new['education']=pd.cut(new.HIEDUC,bins=[0,3,4,7,11],labels=['below_hs','hs','some_college','ba_plus'])
 # Ever-sex recode: 2022-23 RHADSEX 0 (don't know/refused) is imputed as 'No' in HADSEX.
 old['rhadsex_unknown']=False
 new['rhadsex_unknown']=new.RHADSEX.eq(0)
 for d in [old,new]:
  d['age']=d.AGER
  d['race']=pd.Categorical(d.HISPRACE2,categories=[1,2,3,4])
  d['education']=pd.Categorical(d.education,categories=['below_hs','hs','some_college','ba_plus'])
  d['y']=(d.HADSEX==2).astype(float)
  d['poverty_grp']=pd.cut(d.POVERTY,bins=[0,99,199,399,float('inf')],labels=['<100%','100-199%','200-399%','400%+'])
  # strict orientation, comparable age cohort
  d['eligible']=d.straight&d.age.between(18,29)&d.w.gt(0)&d['race'].notna()&d['education'].notna()
 old=old.loc[old.eligible].copy().reset_index(drop=True)
 new=new.loc[new.eligible].copy().reset_index(drop=True)
 # FTF vs web additional response flags
 return old,new

def Xmat(d,with_mode=False, with_poverty=False, with_marital=False):
 age=(d.age.to_numpy()-23.5)
 matr=[np.ones(len(d)),age/5,age**2/25]
 names=['intercept','age_centered','age_sq']
 for k in [2,3,4]:matr.append(d.race.eq(k).astype(float).to_numpy());names.append(f'race{k}')
 for k in ['hs','some_college','ba_plus']:matr.append(d.education.eq(k).astype(float).to_numpy());names.append(f'edu_{k}')
 if with_poverty:
  for k in ['100-199%','200-399%','400%+']:matr.append(d.poverty_grp.eq(k).astype(float).to_numpy());names.append(f'poverty_{k}')
 if with_marital:
  matr.append(d.married_or_cohab.astype(float).to_numpy());names.append('married_or_cohab')
 if with_mode:matr.append(d['mode'].eq(2).astype(float).to_numpy());names.append('web')
 return np.column_stack(matr),names

def fit_predict(train,reference,mode=None,with_mode=False,extra=False):
 X,terms=Xmat(train,with_mode=with_mode,with_poverty=extra,with_marital=extra)
 X0,_=Xmat(reference,with_mode=with_mode,with_poverty=extra,with_marital=extra)
 if mode is not None and with_mode:X0[:,-1]=1 if mode==2 else 0
 w=train['ww'].to_numpy().astype(float); w=w*len(w)/w.sum()
 try:
  mod=sm.GLM(train.y.to_numpy(),X,family=sm.families.Binomial(),freq_weights=w)
  with warnings.catch_warnings():
   warnings.simplefilter('ignore')
   fit=mod.fit(maxiter=100,disp=0)
  if not np.all(np.isfinite(fit.params)):return np.nan
  pred=expit(X0 @ fit.params)
  rw=reference.ww.to_numpy();return float(np.sum(pred*rw)/np.sum(rw))
 except Exception:return np.nan

def resample_mult(d,rng):
 # Rao-Wu rescaled bootstrap: within each stratum select m-1 of m PSUs with replacement
 # then weight selection counts by m/(m-1); original weight array unchanged.
 factors=np.zeros(len(d)); grouped=d.groupby('strat',sort=False,observed=True).indices
 for s,ids in grouped.items():
  psus,inv=np.unique(d.iloc[ids].psu.to_numpy(),return_inverse=True);m=len(psus)
  if m<2:raise ValueError('PSU singleton')
  nums=rng.integers(0,m,size=m-1);counts=np.bincount(nums,minlength=m)
  factors[ids]=counts[inv]*m/(m-1)
 return factors

def mode_tab(d):
 z=[]
 for mode in [1,2]:
  t=d[d['mode']==mode]
  for v in ['age','race','education','poverty_grp','married_or_cohab']:
   if v=='age':
    value=float(np.sum(t.age*t.w)/sum(t.w));z.append(dict(mode=mode,variable='age_mean',category='years',weighted_pct_or_value=value,n=int(len(t))))
   else:
    for cat,g in t.groupby(v,observed=True):z.append(dict(mode=mode,variable=v,category=str(cat),weighted_pct_or_value=100*g.w.sum()/t.w.sum(),n=int(len(g))))
 return pd.DataFrame(z)

def wmean(d):return float(np.dot(d.y,d.ww)/d.ww.sum())

def estimates(a,b):
 a=a.copy();b=b.copy()
 ref=a
 # Direct prevalence
 out={'historic_raw':wmean(a),'new_raw':wmean(b),'new_ftf_raw':wmean(b[b['mode']==1]),'new_web_raw':wmean(b[b['mode']==2])}
 # age, race, educational standardized wave estimates, using 2017-2019 weighted reference
 out['historic_std']=fit_predict(a,ref)
 out['new_std']=fit_predict(b,ref)
 # 2022 FTF & web individually standardized to 2017-19 covariates
 out['ftf_std_2017']=fit_predict(b[b['mode']==1],ref)
 out['web_std_2017']=fit_predict(b[b['mode']==2],ref)
 # 2022 mode difference, standardized over 2022 covariates (pooled logistic)
 out['ftf_std_2022']=fit_predict(b,b,mode=1,with_mode=True)
 out['web_std_2022']=fit_predict(b,b,mode=2,with_mode=True)
 # additional adjustment includes living-with-woman status and poverty; desc only
 out['ftf_ext_2022']=fit_predict(b,b,mode=1,with_mode=True,extra=True)
 out['web_ext_2022']=fit_predict(b,b,mode=2,with_mode=True,extra=True)
 # recompute no sex excluding unknown RHADSEX=0 in new wave
 new_exclude=b.loc[~b.rhadsex_unknown]
 out['new_raw_excl_unknown']=wmean(new_exclude)
 out['ftf_raw_excl_unknown']=wmean(new_exclude[new_exclude['mode']==1])
 out['web_raw_excl_unknown']=wmean(new_exclude[new_exclude['mode']==2])
 return out

def main():
 a,b=build()
 for d in [a,b]:
  d['married_or_cohab']=d.RMARITAL.isin([1,2])
  d['ww']=d.w.astype(float)
 print('n historic/new',len(a),len(b),'new 2022 FTF/web',b['mode'].value_counts().to_dict())
 print('unknown RHADSEX 2022 18-29',int(b.rhadsex_unknown.sum()))
 print('new original y wt',wmean(b),'original old',wmean(a))
 comp=mode_tab(b);comp.to_csv(OUT/'mode_composition_2022.csv',index=False)
 original=estimates(a,b); print('ORIGINAL RESULTS',json.dumps(original,indent=2))
 rng=np.random.default_rng(SEED)
 boot=[]
 for it in range(N_BOOT):
  a['ww']=a.w*resample_mult(a,rng);b['ww']=b.w*resample_mult(b,rng)
  if a.ww.sum()<=0 or b.ww.sum()<=0 or b.loc[b['mode']==1,'ww'].sum()<=0 or b.loc[b['mode']==2,'ww'].sum()<=0:continue
  res=estimates(a,b)
  if np.isfinite(list(res.values())).all():boot.append(res)
  if (it+1)%100==0:print('BOOT',it+1,'valid',len(boot),flush=True)
 boot=pd.DataFrame(boot);boot.to_csv(OUT/'bootstrap_estimates.csv',index=False,float_format='%.7f')
 dd={
  'cross_wave_raw':('new_raw','historic_raw'),
  'cross_wave_adjusted':('new_std','historic_std'),
  'web_ftf_raw':('new_web_raw','new_ftf_raw'),
  'web_ftf_adjusted_2022':('web_std_2022','ftf_std_2022'),
  'web_ftf_extended_2022':('web_ext_2022','ftf_ext_2022'),
  'ftf_2022_vs_2017_raw':('new_ftf_raw','historic_raw'),
  'ftf_2022_vs_2017_std':('ftf_std_2017','historic_std'),
  'web_2022_vs_2017_std':('web_std_2017','historic_std'),
 }
 rows=[]
 for key,(lhs,rhs) in dd.items():
  obs=original[lhs]-original[rhs];vals=(boot[lhs]-boot[rhs]).dropna().to_numpy();lo,hi=np.quantile(vals,[0.025,0.975]);se=vals.std(ddof=1)
  rows.append(dict(contrast=key,delta_pp=obs*100,ci95_low_pp=lo*100,ci95_high_pp=hi*100,bootstrap_se_pp=se*100,replicates=len(vals)))
 pd.DataFrame(rows).to_csv(OUT/'comparison_results.csv',index=False,float_format='%.5f')
 pd.DataFrame([dict(metric=k,rate_pct=v*100) for k,v in original.items()]).to_csv(OUT/'point_estimates.csv',index=False,float_format='%.5f')
 print('COMPARISONS\n',pd.DataFrame(rows).to_string(index=False,float_format=lambda x:f'{x:.2f}'))
 print('COMPOSITION\n',comp[comp.variable.isin(['age_mean','race','education','married_or_cohab'])].to_string(index=False,float_format=lambda x:f'{x:.2f}'))
 with open(OUT/'run_metadata.json','w') as f:json.dump({'seed':SEED,'boot_reps_requested':N_BOOT,'boot_reps_valid':len(boot),'historic_n':len(a),'new_n':len(b),'new_raw_unknown_n':int(b.rhadsex_unknown.sum()),'estimand':'weighted linearization within strata PSU rescaled bootstrap + model-based g-computation; mode contrasts noncausal'},f,indent=2)
if __name__=='__main__':main()
