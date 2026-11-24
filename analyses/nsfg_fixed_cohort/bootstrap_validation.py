"""Independent stratified PSU rescaled bootstrap check for fixed-cohort contrasts."""
from pathlib import Path
import pandas as pd,numpy as np
import analyze as A
OUT=Path(__file__).resolve().parent/'output'
R=1600;rng=np.random.default_rng(20261123)
def reps(frame,cohort):
 d=frame.copy(); dom=d.cohort5.eq(cohort)&d.age.ge(21)&d.event_age_valid
 d['ww']=np.where(dom,d.wt,0);d['wy']=np.where(dom,d.wt*d.never_before_21,0)
 g=d.groupby(['stratum','psu'],sort=False)[['ww','wy']].sum()
 a=np.zeros(R);b=np.zeros(R)
 for s,h in g.groupby(level=0):
  p=h[['ww','wy']].to_numpy();m=len(p)
  assert m>=2
  sel=rng.integers(0,m,size=(R,m-1));sums=p[sel].sum(axis=1)*m/(m-1)
  a+=sums[:,0];b+=sums[:,1]
 return 100*b/a
res=[]
for cohort in ['1985–89','1990–94']:
 old=reps(A.frames['2017_2019'],cohort);new=reps(A.frames['2022_2023'],cohort);dif=new-old
 res.append({'cohort':cohort,'bootstrap_replicates':R,'delta_mean_pp':dif.mean(),'se_pp':dif.std(ddof=1),'ci95_percentile_low_pp':np.quantile(dif,.025),'ci95_percentile_high_pp':np.quantile(dif,.975)})
print(pd.DataFrame(res).to_string(index=False,float_format=lambda x:f'{x:.3f}'))
pd.DataFrame(res).to_csv(OUT/'bootstrap_validation.csv',index=False)
