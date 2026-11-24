from pathlib import Path
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output'; d=pd.read_csv(OUT/'prevalence_all.csv'); s=pd.read_csv(OUT/'sensitivity_modes_weights.csv')

def errbars(a,xx,ax,label):
 ax.errorbar(xx,a.estimate_pct, yerr=[(a.estimate_pct-a.ci95_low_pct).clip(lower=0).to_numpy(),(a.ci95_high_pct-a.estimate_pct).clip(lower=0).to_numpy()],marker='o',capsize=3,linewidth=1.4,label=label)

fig,ax=plt.subplots(figsize=(10,5.3))
years=['2008','2010','2012','2014','2016','2018','2021','2022','2024']
for o,lab in [('zero_partners_12mo','No sex partners, previous 12 months'),('zero_female_since18','Zero female partners since age 18')]:
 a=d[(d.dataset=='GSS')&(d.outcome==o)&(d.population=='all men')&(d.age_group=='18–29')].copy();a['ix']=a.wave.map({x:i for i,x in enumerate(years)});a=a.sort_values('ix')
 errbars(a,a.ix,ax,lab)
ax.set_xticks(range(len(years)),years);ax.set_ylabel('Weighted percentage (95% survey-design CI)');ax.set_xlabel('GSS wave');ax.set_title('GSS: two different measures of young men’s sexual inactivity, ages 18–29')
ax.legend(fontsize=9,loc='upper left');ax.grid(axis='y',alpha=.25);ax.set_ylim(bottom=0);fig.tight_layout();fig.savefig(OUT/'gss_trends.png',dpi=180);plt.close(fig)

fig,ax=plt.subplots(figsize=(10,5.3))
ns=d[(d.dataset=='NSFG')&(d.outcome=='never_vaginal')&(d.population=='heterosexual men')&(d.age_group=='18–29')].copy()
x=np.arange(5)
errbars(ns,x,ax,'All interview modes (weighted)')
s2=s[(s.source=='NSFG')&(s.wave=='2022_2023')&(s.group=='18–29')]
for mode,idx,label in [('face_to_face_straight',4.13,'2022–23: face-to-face only'),('web_straight',4.26,'2022–23: web only')]:
 a=s2[s2.variant==mode];errbars(a,np.array([idx]),ax,label)
ax.axvline(3.5,linewidth=1,linestyle='--',alpha=.5)
ax.text(3.52,40,'Method change',fontsize=9,rotation=90,va='top')
ax.set_xticks(x,['2011–13','2013–15','2015–17','2017–19','2022–23']);ax.set_xlim(-.3,4.62)
ax.set_ylabel('Weighted percentage (95% survey-design CI)');ax.set_xlabel('NSFG wave');ax.set_ylim(0,47)
ax.set_title('NSFG: heterosexual men aged 18–29 reporting no lifetime vaginal intercourse')
ax.legend(fontsize=9,loc='upper left');ax.grid(axis='y',alpha=.25)
fig.tight_layout();fig.savefig(OUT/'nsfg_trends_and_mode.png',dpi=180);plt.close(fig)
print('created figures')
