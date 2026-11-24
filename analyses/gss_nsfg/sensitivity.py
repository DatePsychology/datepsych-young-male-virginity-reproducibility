"""Post-replication diagnostics: sex-orientation, weight, invalid responses, NSFG 2022 mode, age standardization."""
from replicate_full import get_gss,get_new_nsfg,get_old_nsfg,estimate,ROOT,OUT
import pandas as pd,numpy as np,math
from scipy.stats import t as tdist
rows=[]
x=get_gss()
x['wt_new']=x.wtssnrps
x['wt_old']=x.wtss
x['unzero']=np.where(x.numwomen.notna(),x.numwomen.eq(0).astype(float),np.nan)
for year in [2018,2021]:
 y=x[x.year==year]
 for lo,hi in [(18,30),(18,19),(18,20),(26,30),(25,30)]:
  for variant,weight in [('article_naive_wtss','wt_old'),('article_naive_wtssps','wtssps'),('naive_nrps','wt_new'),('clean_nrps','wt_new'),('clean_wtssps','wtssps')]:
   outcome='unzero' if variant!='clean_nrps' and variant!='clean_wtssps' else 'zero_female_since18'
   dom=y.male & y.straight & y.age.between(lo,hi)
   if not y.loc[dom,weight].notna().any():continue
   q=estimate(y,outcome,dom,wt=weight)
   if q:rows.append(dict(source='GSS',wave=year,group=f'{lo}–{hi}',variant=variant,**q))
for year in ['2017_2019','2022_2023']:
 y=get_old_nsfg(year) if year=='2017_2019' else get_new_nsfg()
 if year=='2022_2023':modes=[('all',pd.Series(True,index=y.index)),('face_to_face',y.FTFMODE.eq(1)),('web',y.FTFMODE.eq(2))]
 else:modes=[('all',pd.Series(True,index=y.index))]
 for m,mode in modes:
  for lo,hi in [(18,29),(25,30),(18,24),(22,34)]:
   for straight in [False,True]:
    dom=mode & y.age.between(lo,hi)
    if straight:dom&=y.straight
    q=estimate(y,'never_vaginal',dom)
    if q:rows.append(dict(source='NSFG',wave=year,group=f'{lo}–{hi}',variant=f'{m}_'+('straight' if straight else 'all_men'),**q))
res=pd.DataFrame(rows)
res.to_csv(OUT/'sensitivity_modes_weights.csv',index=False,float_format='%.6f')
for source in ['GSS','NSFG']:
 print('\n',source)
 print(res[res.source==source][['wave','group','variant','n','events','estimate_pct','ci95_low_pct','ci95_high_pct']].to_string(index=False,float_format=lambda v:f'{v:.2f}'))

# Within-age standardization: a fixed empirical weight distribution for ages 18–29.
# Use 2017–2019 NSFG weighted counts (straight men, age) as age reference.
def agestd_nsfg(x,ref):
 # ratio for weighted within-single-age proportion, then combine fixed ref age proportions,
 # a single survey-linearized estimate, not an average of separately reported CIs.
 y=x.copy();y['never_vaginal']=y.never_vaginal.astype(float)
 age_probs=(ref.loc[ref.straight&ref.age.between(18,29)].groupby('age')['wt'].sum());age_probs=age_probs/age_probs.sum()
 # linearized PSU sum (constant target age weights)
 age_stats={}
 for age,q in age_probs.items():
  ind=y.age.eq(age)&y.straight&y.never_vaginal.isin([0,1]);w=y.wt[ind].sum()
  if w<=0:raise ValueError('missing age')
  p=(y.loc[ind,'wt']*y.loc[ind,'never_vaginal']).sum()/w
  age_stats[age]=(p,float(w),float(q))
 pstd=sum(p*q for p,w,q in age_stats.values())
 influence=np.zeros(len(y))
 for age,(p,w,q) in age_stats.items():
  ind=(y.age.eq(age)&y.straight&y.never_vaginal.isin([0,1])).values
  influence+=np.where(ind, q*y.wt*(y.never_vaginal-p)/w,0)
 group=pd.DataFrame({'strat':y.stratum,'psu':y.psu,'u':influence}).groupby(['strat','psu']).u.sum()
 v=0;df=0
 for key,gr in group.groupby(level=0):
  g=gr.to_numpy();m=len(g)
  v+=m/(m-1)*np.sum((g-g.mean())**2);df+=m-1
 se=np.sqrt(v);ci=pstd+np.array([-1,1])*tdist.ppf(.975,df)*se
 return dict(estimate_pct=100*pstd,SE_pp=100*se,ci95_low_pct=100*ci[0],ci95_high_pct=100*ci[1],design_df=df)

ref=get_old_nsfg('2017_2019');r=[]
for wave in ['2011_2013','2013_2015','2015_2017','2017_2019','2022_2023']:
 d=get_old_nsfg(wave) if wave!='2022_2023' else get_new_nsfg()
 q=agestd_nsfg(d,ref)
 r.append(dict(wave=wave,group='heterosexual men 18–29',age_reference='NSFG 2017-2019 heterosexual men 18–29',**q))
pd.DataFrame(r).to_csv(OUT/'nsfg_fixed_age_standardized.csv',index=False,float_format='%.6f')
print('\nAge standardized',r)
