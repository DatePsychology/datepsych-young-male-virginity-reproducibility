#!/usr/bin/env python3
"""Regenerate the nine article figures from archived values (layout may differ) using the accompanying *aggregate* CSV files.

Dependencies: python -m pip install pandas numpy matplotlib
Execute from any folder: python build_figures.py
No respondent-level data are needed.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
OUT=Path(__file__).resolve().parent
D=OUT/'figure_data'
C=OUT/'reproduced_figures'; C.mkdir(exist_ok=True)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.labelsize':12,'xtick.labelsize':11,'ytick.labelsize':11,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':210,'figure.dpi':130})
navy='#193C55'; blue='#3678A2';teal='#297D77';red='#B75B50';gold='#BB8541'; gray='#697988'; purple='#8068A8'; light='#DAE2E9'; bg='#FFFFFF'
C=OUT/'reproduced_figures'
def finish(fig,name):
 fig.savefig(C/name,bbox_inches='tight',pad_inches=.16,facecolor='white');plt.close(fig)

# 01 two panels levels and signed difference.
fig,axes=plt.subplots(2,1,figsize=(10,6.3),gridspec_kw={'height_ratios':[1.35,1]},layout='constrained')
a,b=axes
points=[('2018',22.511869,14.271656,33.642735,blue,1),('2021',16.639466,8.319010,30.512224,teal,0)]
for lab,v,lo,hi,col,y in points:
 a.errorbar(v,y,xerr=[[v-lo],[hi-v]],fmt='o',markersize=11,color=col,lw=2.5,capsize=6)
 a.text(v-1.0,y+.20,f'{v:.1f}%',ha='center',va='center',fontsize=12,fontweight='bold',color=navy)
a.scatter([24.93],[1],marker='o',facecolor='white',edgecolor=red,s=115,lw=2.2,zorder=5)
a.annotate('Original 2018: 24.9%',xy=(24.93,1),xytext=(31.7,1.43),arrowprops=dict(arrowstyle='-',color=red),color=red,fontsize=10)
a.set_yticks([1,0],['2018 (n=124)','2021 (n=87)']);a.set_xlim(0,46);a.set_ylim(-.55,1.65)
a.set_xlabel('Reported no female partners since 18 (%)');a.grid(axis='x',alpha=.16)
b.axvline(0,color=gray,lw=1.6);b.errorbar(-5.8724,.2,xerr=[[14.5676],[14.5724]],fmt='D',ms=9,color=red,capsize=7,lw=2.8)
b.text(-5.8724,.47,'−5.9 pp (95% CI −20.4 to +8.7)',color=navy,ha='center',fontweight='bold',fontsize=11)
b.set_yticks([.2],['2018→2021 change']);b.set_xlim(-25,20);b.set_ylim(-.10,.8);b.set_xlabel('Difference in percentage points; 0 = no change');b.grid(axis='x',alpha=.16)
finish(fig,'01_gss_uncertainty.png')

# 02 YRBS: 2 aligned panels.
yrbs=pd.read_csv(D/'yrbs_prevalence_all.csv')
y=yrbs[yrbs.estimand=='boys_all'].sort_values('year')
miss=pd.read_csv(D/'yrbs_missingness_sensitivity.csv')
miss=miss[miss.population=='boys_all'].sort_values('year')
fig,(a,b)=plt.subplots(2,1,figsize=(10,8.4),sharex=True,gridspec_kw={'height_ratios':[1.5,1]},layout='constrained')
xx=y.year.to_numpy(); yy=y.p.to_numpy()*100; l=y.lo.to_numpy()*100; h=y.hi.to_numpy()*100
a.axvspan(2019.5,2025.6,color='#E7EFF4',alpha=.7,zorder=-1)
a.errorbar(xx,yy,yerr=np.vstack((yy-l,h-yy)),color=blue,marker='o',lw=2.2,markersize=7,capsize=5)
a.scatter([2019,2021],[39.01,32.27],facecolor='white',edgecolor=red,s=120,lw=2,zorder=4)
a.text(2020.0,54.5,'2021–2025: later survey period',fontsize=10,color=gray)
a.annotate('2021 age-standardized: 32.3%',(2021,32.27),xytext=(2020.45,38.1),arrowprops=dict(arrowstyle='-',color=red),color=red,fontsize=11)
a.set_ylabel('Ever had intercourse (%)');a.set_ylim(21,58);a.grid(axis='y',alpha=.18)
a.annotate('2011 49.2%',(2011,49.2),xytext=(2011.2,53.8),fontsize=11,color=navy)
a.annotate('2019 39.2%',(2019,39.2),xytext=(2017.7,46.1),fontsize=11,color=navy,arrowprops=dict(arrowstyle='-',color=navy,alpha=.7))
a.annotate('2025 29.7%',(2025,29.7),xytext=(2022.25,24.5),fontsize=11,color=navy)
b.plot(miss.year,miss.missing_unweighted*100,marker='s',color=red,lw=2.2,label='Unweighted item missingness')
b.plot(miss.year,miss.missing_weighted*100,marker='o',color=teal,lw=2.2,label='Survey-weighted item missingness')
b.set_ylim(0,37);b.set_xticks(xx);b.set_ylabel('Male item unanswered (%)');b.set_xlabel('Survey year');b.grid(axis='y',alpha=.18);b.legend(frameon=False,loc='upper left',fontsize=10.5)
finish(fig,'02_yrbs_boys_trend.png')

# 03 NSFG time-aware trends, + mode subgroup uncertainty.
d=pd.read_csv(D/'gss_nsfg_prevalence_all.csv')
d=d[(d.dataset=='NSFG') & (d.population=='heterosexual men') & (d.age_group=='18–29') & (d.outcome=='never_vaginal')].copy()
mp={'2011–2013':2012,'2013–2015':2014,'2015–2017':2016,'2017–2019':2018,'2022–2023':2022.5}
d['mid']=d.wave.map(mp);d=d.sort_values('mid')
fig,ax=plt.subplots(figsize=(10,6.3),layout='constrained')
ax.axvspan(2022,2025.25,color='#E7EFF4',zorder=-1)
ax.text(2022.08,40,'Redesigned survey',fontsize=10,color=gray)
for _,r in d.iterrows():
 c=red if r.mid>2020 else blue
 ax.errorbar(r.mid,r.estimate_pct,yerr=[[r.estimate_pct-r.ci95_low_pct],[r.ci95_high_pct-r.estimate_pct]],fmt='o',capsize=5,color=c,lw=2,ms=9)
ax.plot(d.mid.to_numpy()[:4],d.estimate_pct.to_numpy()[:4],color=blue,lw=2.0)
ax.errorbar(2022.08,20.87594,yerr=[[20.87594-15.8843],[25.8554-20.87594]],fmt='s',color=teal,lw=2,capsize=5,ms=10)
ax.errorbar(2023.15,30.60947,yerr=[[30.60947-26.3767],[35.0494-30.60947]],fmt='^',color=purple,lw=2,capsize=5,ms=10)
ax.annotate('2022–23 overall 27.5%',(2022.5,27.55),xytext=(2018.9,35.7),arrowprops=dict(arrowstyle='-',color=red),color=red,fontsize=11)
ax.annotate('Face-to-face 20.9%',(2022.08,20.88),xytext=(2019.2,17.6),arrowprops=dict(arrowstyle='-',color=teal),color=teal,fontsize=11)
ax.annotate('Web 30.6%',(2023.15,30.61),xytext=(2023.3,30.6),color=purple,fontsize=11)
ax.set_xlim(2010.8,2025.55);ax.set_ylim(0,42);ax.set_xticks([2012,2014,2016,2018,2022.5],['2011–13','2013–15','2015–17','2017–19','2022–23']);ax.tick_params(axis='x',labelsize=10.5)
ax.set_ylabel('No female vaginal intercourse (%)');ax.set_xlabel('NSFG collection period (calendar spacing)');ax.grid(axis='y',alpha=.18)
finish(fig,'03_nsfg_discontinuity.png')

# 04 cohort both lines intervals.
cohorts=pd.read_csv(D/'nsfg_threshold_prevalence.csv')
q=cohorts[(cohorts.cohort.isin(['1985–89','1990–94']))&(cohorts.threshold=='before 21st birthday')&(cohorts.population=='all men')&(cohorts['mode']=='all')].copy()
q['mid']=q.wave.map(mp)
fig,ax=plt.subplots(figsize=(10,6.3),layout='constrained')
ax.axvspan(2022,2025,color='#E7EFF4',zorder=-1)
ax.text(2022.1,51,'Redesigned survey',fontsize=10,color=gray)
for cohort,clr,offset in [('1985–89',blue,-.12),('1990–94',teal,.12)]:
 t=q[q.cohort==cohort].sort_values('mid')
 if cohort=='1990–94': t=t[t.mid>=2016]
 for historical,part in [(True,t[t.mid<2020]),(False,t[t.mid>=2020])]:
  xp=part.mid.to_numpy()+offset;yp=part.estimate_pct.to_numpy()
  ax.errorbar(xp,yp,yerr=np.vstack((yp-part.ci95_low_pct.to_numpy(),part.ci95_high_pct.to_numpy()-yp)),fmt='o-' if historical else 'o',capsize=4,lw=2,ms=8,color=clr,label='Born '+cohort if historical else None)
ax.set_xlim(2010.7,2025);ax.set_ylim(0,54);ax.set_ylabel('No female vaginal intercourse before 21 (%)')
ax.set_xticks([2012,2014,2016,2018,2022.5],['2011–13','2013–15','2015–17','2017–19','2022–23']);ax.tick_params(axis='x',labelsize=10.5);ax.grid(axis='y',alpha=.17);ax.legend(frameon=False,loc='upper left')
finish(fig,'04_nsfg_fixed_cohort.png')

# 05 Flow diagram; counts only, grounded.
fig,ax=plt.subplots(figsize=(10,6.3));ax.set_axis_off();ax.set_xlim(0,10);ax.set_ylim(0,7.2);ax.text(5,7.0,'Unweighted respondent counts',ha='center',color=gray)
def node(x,y,w,h,big,small,clr):
 patch=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.13,rounding_size=.16',fc=clr,ec='#BDCBD5',lw=1)
 ax.add_patch(patch);ax.text(x+w/2,y+h*.65,big,ha='center',va='center',fontsize=19,weight='bold',color=navy);ax.text(x+w/2,y+h*.25,small,ha='center',va='center',fontsize=10.3,color=navy)
def arrow(p1,p2):ax.annotate('',xy=p2,xytext=p1,arrowprops=dict(arrowstyle='-|>',lw=1.6,color=gray))
node(2.9,5.75,4.2,.90,'938','Age-15 eligible: no intercourse', '#E4EEF4')
node(.5,3.65,4.0,.95,'697','Usable young-adult vaginal status','#E2F1EB')
node(5.45,3.65,4.0,.95,'241','Outcome unavailable','#F4E8E5')
arrow((4.35,5.75),(2.52,4.6));arrow((5.6,5.75),(7.45,4.6))
node(.45,1.58,3.8,.94,'514','Adult reported vaginal intercourse','#E4F2F0')
node(5.6,1.58,3.85,.94,'183','Adult reported no vaginal intercourse','#EDF1F4')
arrow((2.52,3.65),(2.35,2.52));arrow((2.64,3.65),(7.52,2.52))
node(.52,.13,3.7,.72,'503','Valid debut age','#EAF1F6')
node(5.62,.13,3.7,.72,'11','Debut age unavailable','#F6EFE2')
arrow((2.35,1.58),(2.35,.85));arrow((2.45,1.58),(7.4,.85))
finish(fig,'05_ffcws_flow.png')

# 06 categorized bars with CIs for n=938, source data
q=pd.read_csv(D/'chronology_components.csv').set_index('category')
cats=[('Reported debut age definitely later','reported_age_strictly_after_y15',teal),('Adult outcome unavailable','adult_vaginal_outcome_missing',gray),('Adult reported no vaginal','adult_known_no_vaginal',blue),('Same completed age','reported_same_completed_age',gold),('Reported debut earlier','reported_age_earlier_than_y15',red),('Debut age unavailable','adult_vaginal_yes_age_missing',purple)]
fig,ax=plt.subplots(figsize=(10,6.3),layout='constrained')
for i,(name,key,col) in enumerate(cats):
 r=q.loc[key]; yidx=len(cats)-1-i;p=r['share']*100;lo=r.ci_low*100;hi=r.ci_high*100
 ax.barh(yidx,p,height=.59,color=col,alpha=.9);ax.errorbar(p,yidx,xerr=[[p-lo],[hi-p]],fmt='none',ecolor=navy,capsize=4,lw=1.9)
 ax.text(max(p+1.25,hi+1),yidx,f'{p:.1f}%  (n={int(r.n_event)})',va='center',fontsize=11,color=navy)
ax.set_yticks(range(6),[x[0] for x in cats][::-1]);ax.set_xlim(0,72);ax.set_xticks([0,15,30,45,60]);ax.set_xlabel('Survey-weighted share of original domain (%); n = unweighted counts');ax.grid(axis='x',alpha=.17)
finish(fig,'06_ffcws_histories.png')


# 07. Qualitative measure comparison (not numerical data).
from textwrap import fill
s=pd.read_csv(D/'survey_measures.csv')
fig,ax=plt.subplots(figsize=(11,8.2),layout='constrained');ax.axis('off')
ax.set_title('What each survey measures and cannot establish',loc='left',weight='bold',color=navy,pad=14)
for i,r in s.iterrows():
 y=.91-i*.18
 ax.text(.02,y,r.source,transform=ax.transAxes,weight='bold',color=navy,va='top')
 ax.text(.29,y,fill(r.measure,34),transform=ax.transAxes,va='top',fontsize=11)
 ax.text(.65,y,fill(r.limitation,32),transform=ax.transAxes,va='top',fontsize=11)
 ax.plot([.02,.98],[y-.15,y-.15],transform=ax.transAxes,color=light,lw=1)
finish(fig,'07_survey_measures.png')
# 08. YRBS observed estimates, MAR and MNAR model scenarios, and worst-case bounds.
m=pd.read_csv(OUT/'analyses/yrbs_nsfg/output/yrbs_missingness_age_grade_MNAR.csv').set_index('year')
z=miss.set_index('year')
fig,ax=plt.subplots(figsize=(10,5.5),layout='constrained')
for year,col,off in [(2011,blue,.13),(2019,red,-.13)]:
 r=m.loc[year]; b=z.loc[year]; xx=[(r.observed_rate,r.observed_rate),(r.age_grade_MAR,r.age_grade_MAR),(r.MNAR_OR_0_5,r.MNAR_OR_2),(b.min_bound,b.max_bound)] if 'MNAR_OR_0_5' in r.index else [(r.observed_rate,r.observed_rate),(r.age_grade_MAR,r.age_grade_MAR),(r['MNAR_OR_0.5'],r.MNAR_OR_2),(b.min_bound,b.max_bound)]
 for i,(lo,hi) in enumerate(xx):
  y=3-i+off;lo*=100;hi*=100
  if lo==hi: ax.scatter(lo,y,color=col,s=70,label=str(year) if i==0 else None); lab=f'{lo:.1f}%'
  else: ax.hlines(y,lo,hi,color=col,lw=5);ax.plot([lo,hi],[y,y],'|',color=col,ms=10);lab=f'{lo:.1f}–{hi:.1f}%'
  ax.text(hi+.3,y,lab,va='center',color=col,fontsize=10)
ax.set_yticks(range(4),['Worst-case bounds','MNAR odds ×0.5–2','Age/grade MAR','Complete observed responses']);ax.set_xlim(30,58);ax.set_xlabel('Boys reporting lifetime intercourse (%)');ax.legend(frameon=False);ax.grid(axis='x',alpha=.18)
finish(fig,'08_yrbs_sensitivity.png')
# 09. Fixed-cohort milestone contrasts, independent-wave CIs.
t=pd.read_csv(OUT/'analyses/nsfg_fixed_cohort/output/same_cohort_fixed_milestone_contrasts.csv');t=t[(t.cohort=='1985–89')&(t['pop']=='all men')&(t.old=='2017_2019')&(t.new=='2022_2023')].sort_values('threshold')
fig,ax=plt.subplots(figsize=(9,4.7),layout='constrained'); y=np.arange(len(t))[::-1];v=t.difference_pp.to_numpy();lo=t.ci_low_pp.to_numpy();hi=t.ci_high_pp.to_numpy()
ax.errorbar(v,y,xerr=[v-lo,hi-v],fmt='o',color=blue,capsize=4,lw=2,ms=8);ax.axvline(0,color=gray,ls='--')
for yi,a,b,c in zip(y,v,lo,hi):ax.text(c+.4,yi,f'+{a:.2f} pp ({b:.2f} to {c:.2f})',va='center',fontsize=10)
ax.set_yticks(y,[f'Before age {n}' for n in t.threshold]);ax.set_xlim(0,34);ax.set_xlabel('2017–2019 to 2022–2023 change (percentage points)');ax.grid(axis='x',alpha=.18)
finish(fig,'09_nsfg_thresholds.png')
