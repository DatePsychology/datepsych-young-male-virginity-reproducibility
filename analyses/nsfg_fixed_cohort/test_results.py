from pathlib import Path
import pandas as pd, numpy as np
out=Path(__file__).resolve().parent/'output'; x=pd.read_csv(out/'threshold_prevalence_by_wave.csv'); c=pd.read_csv(out/'same_cohort_fixed_milestone_contrasts.csv'); t=pd.read_csv(out/'retrospective_transition_21_to_25.csv')
assert len(x)>200
assert x.estimate_pct.notna().all()
finite = x[x.ci95_low_pct.notna() & x.ci95_high_pct.notna()]
assert (finite.ci95_low_pct<=finite.estimate_pct).all() and (finite.estimate_pct<=finite.ci95_high_pct).all()
assert ((x.estimate_pct>=0)&(x.estimate_pct<=100)).all()
# Retrospective proportions never having had sex must decline as the milestone ages for identical age-eligible samples.
for w in x.wave.unique():
 d=x[(x.wave==w)&(x.age_band=='25–29')&(x.population=='all men')&(x.cohort=='all')&(x['mode']=='all')]
 got=[float(d[d.threshold==f'before {a}{"st" if a==21 else "th"} birthday'].estimate_pct.iloc[0]) for a in [18,21,25]]
 assert got[0]>=got[1]>=got[2],(w,got)
assert len(c)>5
assert len(t)==30
print('PASSED: sample integrity, monotone retrospective status, survey intervals, contrast and transition records.')
