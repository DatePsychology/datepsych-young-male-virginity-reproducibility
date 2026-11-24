from pathlib import Path
import sys, numpy as np,pandas as pd,math
from scipy.stats import t as td
sys.path.insert(0,'/mnt/data/nsfg_adult_transition')
import analyze as A
OUT=Path(__file__).resolve().parent/'output'
rows=[]
# compare same completed ages (before 21 or 25), between waves: normal cross-wave independent approximation
for c in ['1985–89','1990–94','1995–99']:
 for t in [18,21,25]:
  for pop in ['all men','heterosexual men']:
   for w1,w2 in [('2011_2013','2017_2019'),('2015_2017','2017_2019'),('2017_2019','2022_2023')]:
    d1,d2=A.frames[w1],A.frames[w2]
    x1=A.out_est(d1,pop,18,49,t,c);x2=A.out_est(d2,pop,18,49,t,c)
    if not x1 or not x2 or min(x1['n'],x2['n'])<100:continue
    delta=x2['estimate_pct']-x1['estimate_pct'];se=math.hypot(x1['SE_pp'],x2['SE_pp'])
    df=(x1['SE_pp']**2+x2['SE_pp']**2)**2 / (x1['SE_pp']**4/x1['design_df']+x2['SE_pp']**4/x2['design_df'])
    tc=td.ppf(.975,df)
    rows.append(dict(cohort=c,threshold=t,pop=pop,old=w1,new=w2,n_old=x1['n'],n_new=x2['n'],pct_old=x1['estimate_pct'],pct_new=x2['estimate_pct'],difference_pp=delta,ci_low_pp=delta-tc*se,ci_high_pp=delta+tc*se,p_two_sided=2*td.sf(abs(delta/se),df)))
r=pd.DataFrame(rows);r.to_csv(OUT/'same_cohort_fixed_milestone_contrasts.csv',index=False,float_format='%.7f')
print('\nPrespecified 2017-19 to 2022-23 same cohorts')
print(r.query("old=='2017_2019' and pop=='all men' and threshold==21").to_string(index=False,float_format=lambda z:f'{z:.2f}'))
print('\n2011 to 2017 same cohorts, historical stability')
print(r.query("old=='2011_2013' and pop=='all men' and threshold==21").to_string(index=False,float_format=lambda z:f'{z:.2f}'))

modes=[]
d=A.frames['2022_2023']
for c in ['1985–89','1990–94','1995–99']:
 for t in [21,25]:
  for pop in ['all men','heterosexual men']:
   for mode in [1,2]:
    x=A.out_est(d,pop,18,49,t,c,mode=mode)
    if x and x['n']>=30:modes.append(x)
pd.DataFrame(modes).to_csv(OUT/'cohort_by_mode.csv',index=False,float_format='%.7f')
print('\nMode cohort 21')
print(pd.DataFrame(modes).query("population=='all men' and threshold=='before 21st birthday'")[['cohort','mode','n','estimate_pct','ci95_low_pct','ci95_high_pct']].to_string(index=False,float_format=lambda z:f'{z:.2f}'))

# Approx birthyear ±1 category tests; use cohorts of width 3 interior and shifted 5yr groups, all 2017 and new
shifts=[]
for a,b in [(1985,1989),(1986,1988),(1990,1994),(1991,1993),(1984,1990),(1989,1995),(1986,1990),(1991,1995)]:
 for t in [21,25]:
  x=[]
  for w in ['2017_2019','2022_2023']:
   d=A.frames[w];mask=d.approx_birthyear.between(a,b)&d.age.ge(t)&d.event_age_valid
   e=A.estimate(d,f'never_before_{t}',mask)
   if e:x.append((w,e))
  if len(x)==2 and min(z[1]['n'] for z in x)>=80:
   delta=x[1][1]['estimate_pct']-x[0][1]['estimate_pct'];se=math.hypot(x[0][1]['SE_pp'],x[1][1]['SE_pp'])
   shifts.append(dict(cohort_bin=f'{a}–{b}',threshold=t,n_2017=x[0][1]['n'],n_2022=x[1][1]['n'],pct_2017=x[0][1]['estimate_pct'],pct_2022=x[1][1]['estimate_pct'],change_pp=delta,ci_low_pp=delta-1.98*se,ci_high_pp=delta+1.98*se))
pd.DataFrame(shifts).to_csv(OUT/'birthyear_bin_sensitivity.csv',index=False,float_format='%.7f')
print('\nBirth year boundary sensitivity')
print(pd.DataFrame(shifts).query('threshold==21').to_string(index=False,float_format=lambda z:f'{z:.2f}'))
