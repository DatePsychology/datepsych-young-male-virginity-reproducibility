import re, math
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from scipy.stats import t as td
from pathlib import Path
def estimate(frame, outcome, domain, wt='wt',strat='stratum',psu='psu'):
    """With-replacement stratified PSU linearization for weighted mean, domain inference.
    Keep all PSUs in same wave even when no sampled members belong to domain.
    Multiplies strata-specific centered PSU influence by m_h/(m_h-1).
    """
    d=frame.loc[(frame[wt]>0)&frame[wt].notna()&frame[strat].notna()&frame[psu].notna()].copy()
    msk=domain.reindex(d.index).fillna(False)&d[outcome].isin([0,1]); y=d[outcome];n=int(msk.sum());events=int((msk & y.eq(1)).sum())
    if n<1:return None
    w=d[wt]; denom=float(w.loc[msk].sum());p=float((w[msk]*y[msk]).sum()/denom)
    infl=np.where(msk,w*(y.fillna(0)-p)/denom,0)
    group=pd.DataFrame({'s':d[strat].to_numpy(),'u':d[psu].to_numpy(),'lin':infl}).groupby(['s','u'],sort=False).lin.sum()
    var=0.;deg=0;details=[]
    for s,g in group.groupby(level=0):
        a=g.to_numpy();m=len(a)
        if m<2: raise ValueError(f'Singleton design stratum {s}')
        var+=(m/(m-1))*np.sum((a-a.mean())**2); deg+=m-1
        details.append((s,m))
    se=math.sqrt(var);critical=float(td.ppf(.975,deg));
    if p>0 and p<1:
        logse=se/(p*(1-p));lo,hi=expit(logit(p)+np.array([-1,1])*critical*logse)
    else:lo,hi=(np.nan,np.nan)
    return dict(n=n,events=events,estimate_pct=100*p,SE_pp=100*se,ci95_low_pct=100*lo,ci95_high_pct=100*hi,
      wald95_low_pct=100*max(0,p-critical*se),wald95_high_pct=100*min(1,p+critical*se),design_df=deg,
      num_strata=len(details),num_psu=sum(x[1] for x in details),weight_sum=denom)

def fields_from_stata_dictionary(fname,needed):
    t=Path(fname).read_text(encoding='latin1')
    pat=re.compile(r'_column\s*\(\s*(\d+)\s*\)\s+(\w+)\s+(\w+)\s+(%[0-9]+[A-Za-z])',re.I)
    fields={name.upper():(int(pos),typ.lower(),fmt) for pos,typ,name,fmt in pat.findall(t)}
    assert set(needed).issubset(fields),f'{fname} missing {set(needed)-set(fields)}'
    cs=[]
    for k in needed:
        pos,typ,fmt=fields[k];width=int(re.search(r'(\d+)',fmt)[1]);cs.append((pos-1,pos-1+width))
    return cs
