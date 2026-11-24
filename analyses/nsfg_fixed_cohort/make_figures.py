from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent; out=root/'output'
x=pd.read_csv(out/'threshold_prevalence_by_wave.csv')
fig,ax=plt.subplots(figsize=(9,5.1))
for co in ['1985–89','1990–94']:
 s=x[(x.population=='all men')&(x.age_band=='18–49')&(x.cohort==co)&(x.threshold=='before 21st birthday')&(x['mode']=='all')]
 # Rows with cohort use age_band 18-49
 if len(s)==0:
  s=x[(x.population=='all men')&(x.cohort==co)&(x.threshold=='before 21st birthday')&(x['mode']=='all')]
 ax.errorbar(range(len(s)),s.estimate_pct,yerr=[s.estimate_pct-s.ci95_low_pct,s.ci95_high_pct-s.estimate_pct],capsize=3,marker='o',label='Born ~'+co)
ax.set_xticks(range(5),['2011–13','2013–15','2015–17','2017–19','2022–23'])
ax.set_ylabel('No vaginal intercourse before age 21 (%)')
ax.set_title('Fixed historical milestone: different reports across NSFG waves')
ax.set_ylim(0,55);ax.grid(axis='y',alpha=.25);ax.legend()
fig.tight_layout();fig.savefig(out/'fixed_cohort_milestone.png',dpi=180);plt.close(fig)

v=pd.read_csv(out/'threshold_prevalence_by_wave.csv')
fig,ax=plt.subplots(figsize=(8.8,5))
for wave in ['2011–2013','2013–2015','2015–2017','2017–2019','2022–2023']:
 d=v[(v.wave==wave)&(v.population=='all men')&(v.cohort=='all')&(v.age_band=='25–29')&(v['mode']=='all')]
 age=[18,21,25]
 vals=[]
 for a in age:
  vals.append(float(d.loc[d.threshold==f'before {a}{"st" if a==21 else "th"} birthday','estimate_pct'].iloc[0]))
 ax.plot(age,vals,marker='o',label=wave)
ax.set_xlabel('Age milestone (birthday)')
ax.set_xticks([18,21,25]);ax.set_ylabel('Had not yet had vaginal intercourse (%)')
ax.set_title('Retrospective sexual-initiation trajectories among men aged 25–29')
ax.set_ylim(0,65);ax.grid(axis='y',alpha=.25);ax.legend()
fig.tight_layout();fig.savefig(out/'adult_catchup.png',dpi=180);plt.close(fig)
