#!/usr/bin/env python3
"""NSFG male age-at-first heterosexual vaginal intercourse adult-transition audit.
All primary estimates are within-wave design-adjusted. Birth years approximate (age is whole years).
Threshold age T means *before Tth birthday*: VRY1STAG < T. Population: men age >= T at interview.
"""
from pathlib import Path
import re,glob,io,zipfile,sys,math,json,os
import numpy as np
import pandas as pd
from scipy.stats import t as tdist
ROOT=Path(os.getenv('NSFG_DATA_ROOT',str(Path(__file__).resolve().parent/'input')))
OUT=Path(__file__).resolve().parent/'output'; OUT.mkdir(exist_ok=True)
from survey_utils import fields_from_stata_dictionary, estimate
WAVES=['2011_2013','2013_2015','2015_2017','2017_2019','2022_2023']
COLS=['AGER','HADSEX','VRY1STAG','CMINTVW','SEST','SECU','FTFMODE','ORIENT','ORIENT_A','ORIENT_B']

def load(w):
    if w=='2022_2023':
        z=zipfile.ZipFile(ROOT/'NSFG-2022-2023-MaleRespPUFData.zip');
        use=['AGER','HADSEX','vry1stag','CMINTVW','VEST','VECL','WGT2022_2023','ORIENT','FTFMODE']
        d=pd.read_csv(io.BytesIO(z.read(z.namelist()[0])),usecols=use)
        d.rename(columns={'vry1stag':'VRY1STAG','VEST':'stratum','VECL':'psu','WGT2022_2023':'wt'},inplace=True)
        d['straight']=d.ORIENT.eq(2)
    else:
        dic=glob.glob(str(ROOT/f'{w}_MaleSetup*.dct'))[0]
        use=['AGER','HADSEX','VRY1STAG','CMINTVW','SEST','SECU',f'WGT{w}']
        if w in ['2015_2017','2017_2019']:use+=['ORIENT_A','ORIENT_B']
        else:use+=['ORIENT']
        d=pd.read_fwf(ROOT/f'{w}_MaleData.dat',colspecs=fields_from_stata_dictionary(dic,use),names=use)
        d.rename(columns={'SEST':'stratum','SECU':'psu',f'WGT{w}':'wt'},inplace=True)
        d['straight']=d.ORIENT.eq(1) if 'ORIENT' in d else (d.ORIENT_A.eq(1)|d.ORIENT_B.eq(2))
        d['FTFMODE']=np.nan
    for c in ['AGER','HADSEX','VRY1STAG','CMINTVW','wt','stratum','psu']:d[c]=pd.to_numeric(d[c],errors='coerce')
    d['age']=d.AGER
    d['interview_year']=1900+((d.CMINTVW-1)//12).astype(int)
    d['approx_birthyear']=d.interview_year-d.age
    d['cohort5']=pd.cut(d.approx_birthyear,bins=[1960,1974,1979,1984,1989,1994,1999,2004,2009,2015],labels=['<=1974','1975–79','1980–84','1985–89','1990–94','1995–99','2000–04','2005–09','2010+'])
    # VRY1STAG value is completed years old at first heterosexual vaginal intercourse.
    # For adults who have not yet had intercourse, it is missing by design.
    d['event_age']=np.where((d.HADSEX==1)&d.VRY1STAG.between(0,60),d.VRY1STAG,np.nan)
    d['age_date_conflict']=(d.HADSEX.eq(1)&d.event_age.notna()&(d.event_age>d.age))
    d['event_age_valid']=(d.HADSEX.eq(2)|(d.HADSEX.eq(1)&d.event_age.notna()&~d.age_date_conflict))
    for t in [18,20,21,22,25,30]:
        d[f'never_before_{t}']=np.where(d.event_age_valid, (d.HADSEX.eq(2)|(d.event_age>=t)).astype(float),np.nan)
    d['never_current']=np.where(d.HADSEX.isin([1,2]),d.HADSEX.eq(2).astype(float),np.nan)
    d['wave']=w.replace('_','–')
    return d

def adjusted_cov(x,y,dom,dom2=None):
    # design linearization for the pair of weighted means and covariance; domain=common domain normally.
    v=x.loc[x.wt.gt(0)&x.wt.notna()&x.stratum.notna()&x.psu.notna()].copy();
    if dom2 is None:dom2=dom
    dom=dom.reindex(v.index).fillna(False)&v[y[0]].isin([0,1]);dom2=dom2.reindex(v.index).fillna(False)&v[y[1]].isin([0,1]);
    means=[];infs=[]
    for c,sel in zip(y,[dom,dom2]):
        weight_sum=float(v.loc[sel,'wt'].sum());p=float(np.average(v.loc[sel,c],weights=v.loc[sel,'wt']))
        means.append(p);infs.append(np.where(sel,v.wt*(v[c].fillna(0)-p)/weight_sum,0))
    z=pd.DataFrame({'stratum':v.stratum,'psu':v.psu,'z1':infs[0],'z2':infs[1]}).groupby(['stratum','psu'],sort=False)[['z1','z2']].sum()
    cv=np.zeros((2,2));deg=0
    for _,h in z.groupby(level=0):
        a=h.to_numpy();m=len(a)
        if m<=1:continue
        cv+=(m/(m-1))*(a-a.mean(axis=0)).T @ (a-a.mean(axis=0));deg+=m-1
    return means,cv,deg

def out_est(d,pop,age_lo,age_hi,threshold,cohort=None,mode=None):
    mask=d.age.between(age_lo,age_hi)
    if pop=='heterosexual men': mask &=d.straight
    if threshold:
        mask&=d.age.ge(threshold)
    if cohort:mask&=d.cohort5.eq(cohort)
    if mode:mask&=d.FTFMODE.eq(mode)
    o='never_current' if threshold is None else f'never_before_{threshold}'
    e=estimate(d,o,mask)
    if not e: return None
    return {'wave':d.wave.iloc[0],'population':pop,'age_band':f'{age_lo}–{age_hi}', 'threshold':(f'before {threshold}{"st" if threshold==21 else "nd" if threshold==22 else "th"} birthday' if threshold else 'as of interview'),'cohort':cohort or 'all', 'mode':mode or 'all',**e}

frames={w:load(w) for w in WAVES}
print('load summary')
for w,d in frames.items():
 print(w,'n',len(d),'age21',sum(d.age>=21),'age25',sum(d.age>=25),'had',d.HADSEX.value_counts().to_dict(),'age at first invalid',sum(d.HADSEX.eq(1)&d.event_age.isna()),'date contradictions',int(d.age_date_conflict.sum()),'year',d.interview_year.value_counts().to_dict())

res=[]
for w,d in frames.items():
 for pop in ['all men','heterosexual men']:
    for age_lo,age_hi in [(18,29),(20,24),(25,29),(25,34),(30,39),(18,34)]:
        for t in [18,20,21,22,25,30,None]:
            if t and age_hi<t:continue
            e=out_est(d,pop,age_lo,age_hi,t)
            if e:res.append(e)
    for cohort in ['1980–84','1985–89','1990–94','1995–99','2000–04','2005–09']:
        for t in [18,20,21,25,30]:
            e=out_est(d,pop,18,49,t,cohort)
            if e and e['n']>=30:res.append(e)
            # For cohort same age 'matured' only if all at age threshold: cohort mix within wave otherwise indicate n.
    if w=='2022_2023':
        for mode in [1,2]:
            for lo,hi in [(20,24),(25,29),(25,34),(30,39)]:
                for t in [20,21,25,None]:
                    if t and hi<t:continue
                    e=out_est(d,pop,lo,hi,t,mode=mode)
                    if e and e['n']>=30:res.append(e)
res=pd.DataFrame(res);res.to_csv(OUT/'threshold_prevalence_by_wave.csv',index=False,float_format='%.8f')

# Conditional initiation between age 21 and 25 among men age 25-29.
# This estimates what fraction of men who had not had vaginal intercourse by their 21st birthday initiated before the 25th.
trans=[]
for w,d in frames.items():
  for pop in ['all men','heterosexual men']:
   for a,b in [(25,29),(25,34),(30,39)]:
    mask=d.age.between(a,b)&d.age.ge(25)&d.event_age_valid
    if pop=='heterosexual men':mask&=d.straight
    mn,cv,df=adjusted_cov(d,['never_before_21','never_before_25'],mask)
    p21,p25=mn
    newly=p21-p25
    cond=(p21-p25)/p21 if p21>0 else np.nan
    grad=np.array([p25/p21**2,-1/p21]) if p21>0 else np.array([np.nan,np.nan]);se_cond=float(np.sqrt(grad@cv@grad))
    diffvar=float(np.array([1,-1])@cv@np.array([1,-1]));se_diff=math.sqrt(max(0,diffvar));tc=tdist.ppf(.975,df)
    trans.append(dict(wave=d.wave.iloc[0],pop=pop,age_band=f'{a}–{b}',n=int(mask.sum()),p_no_sex_by21=100*p21,p_no_sex_by25=100*p25,initiated_ages21_24_pp=100*newly,ci_low_change_pp=100*(newly-tc*se_diff),ci_high_change_pp=100*(newly+tc*se_diff),conditional_initiation_pct=100*cond,conditional_ci_low_pct=max(0,100*(cond-tc*se_cond)),conditional_ci_high_pct=min(100,100*(cond+tc*se_cond)),SE_conditional_pp=100*se_cond,df=df))
pd.DataFrame(trans).to_csv(OUT/'retrospective_transition_21_to_25.csv',index=False,float_format='%.7f')

# Within-wave birth-cohort contrast at fixed threshold using independent stratum full-frame
# cohort labels approximate with +/-1 year, report n and per-wave CIs, plus wave-specific contrast.
contr=[]
for w,d in frames.items():
 for pop in ['all men','heterosexual men']:
  for t in [18,20,21,25]:
   for c1,c2 in [('1985–89','1990–94'),('1990–94','1995–99'),('1995–99','2000–04')]:
    def m(c):
     x=d.age.ge(t)&d.cohort5.eq(c)&d.event_age_valid
     if pop=='heterosexual men':x&=d.straight
     return x
    if m(c1).sum()<35 or m(c2).sum()<35:continue
    est1,est2=estimate(d,f'never_before_{t}',m(c1)),estimate(d,f'never_before_{t}',m(c2))
    mean,cov,df=adjusted_cov(d,[f'never_before_{t}',f'never_before_{t}'],m(c1),m(c2))
    diff=mean[1]-mean[0];grad=np.array([-1,1]);se=float(np.sqrt(grad@cov@grad));tc=tdist.ppf(.975,df)
    contr.append(dict(wave=d.wave.iloc[0],pop=pop,threshold=t,cohort_old=c1,cohort_new=c2,n_old=est1['n'],n_new=est2['n'],pct_old=100*mean[0],pct_new=100*mean[1],change_pp=100*diff,ci_low_pp=100*(diff-tc*se),ci_high_pp=100*(diff+tc*se),p=float(2*tdist.sf(abs(diff/se),df)) if se>0 else np.nan))
pd.DataFrame(contr).to_csv(OUT/'within_wave_cohort_contrasts.csv',index=False,float_format='%.7f')

print('\nThresholds all 25-29')
print(res[(res.population=='all men')&(res.age_band=='25–29')&(res.cohort=='all')&(res['mode']=='all')][['wave','threshold','n','estimate_pct','ci95_low_pct','ci95_high_pct']].to_string(index=False,float_format=lambda z:f'{z:.2f}'))
print('\nTransitions')
print(pd.DataFrame(trans).query("pop=='all men' and age_band=='25–29'").to_string(index=False,float_format=lambda z:f'{z:.2f}'))
print('\nHistorical within wave contrast')
cc=pd.DataFrame(contr)
print(cc.query("pop=='all men' and threshold==21").to_string(index=False,float_format=lambda z:f'{z:.2f}'))
