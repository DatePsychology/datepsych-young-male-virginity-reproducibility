"""Synthetic local check, NOT a study result."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json
import numpy as np
import pandas as pd
from ffcws_attrition_reference import run, classify, estimate_scenarios, covariate_matrix

def test():
    rng=np.random.default_rng(20261123); n=1900
    mom_edu=rng.choice([1,2,3,4],n,p=[.2,.35,.25,.2]);race=rng.choice([1,2,3,4],n)
    mom_age=rng.normal(26,6,n).clip(15,48)
    male=rng.binomial(1,.55,n).astype(bool)
    early_yes=rng.binomial(1,.26,n).astype(bool)
    y15partner=rng.binomial(1,.18,n).astype(bool)&early_yes
    y15b=np.where(early_yes & ~y15partner,1,np.where(y15partner,-6,2))
    y15a=np.where(y15partner,1,2)
    # Data generating: demographic predictors are associated with both adult sex and follow-up.
    p_y=1/(1+np.exp(-(-.6 + .47*mom_edu + .4*early_yes)))
    ever=rng.binomial(1,p_y,n)
    p_obs=1/(1+np.exp(-(-1.0 + .48*mom_edu + .08*mom_age/10)))
    present=rng.binomial(1,p_obs,n).astype(bool)
    d=pd.DataFrame({'cm1bsex':np.where(male,1,2),'k6f19':y15a,'k6f26':y15b,
        'k7e58':np.where(present,np.where(ever,1,2),-9),
        'k7e59':np.where(present & (ever==1),1,-6),
        'cm1age':mom_age,'cm1edu':mom_edu,'cm1ethrace':race,
        'cm1relf':rng.choice([1,2,3],n),'cm1povca':rng.choice([1,2,3,4],n),
        'ck6childageinterviewm':rng.normal(184,8,n)})
    w6=rng.uniform(.3,3.,n);w6[rng.random(n)<.15]=0
    w7=w6*rng.uniform(.8,1.3,n);w7[rng.random(n)<.12]=0
    d['k6natwt']=w6;d['k7natwt']=w7
    for i in range(1,34):
        d[f'k6natwt_rep{i}']=w6*rng.uniform(.94,1.06,n)
        d[f'k7natwt_rep{i}']=w7*rng.uniform(.94,1.06,n)
    with TemporaryDirectory() as tmp:
        path=Path(tmp)/'synthetic_data.csv'
        out=Path(tmp)/'results'
        d.to_csv(path,index=False)
        args=SimpleNamespace(allwaves=str(path),out=str(out),male_code=1,clip=.02,
                       odds='.25,.5,1,2,4',disclosure_n=15,checksum=False)
        run(args)
        a=pd.read_csv(out/'estimates.csv')
        b=pd.read_csv(out/'mnar_sensitivity.csv')
        c=json.loads((out/'audit_summary.json').read_text())
        names=set(a['method'])
        assert {'original_y22_national_complete_case','ipw_mar','aipw_mar','imputed_mnar_odds_1','bounds_lower','bounds_upper'} <= names
        lower=float(a.loc[a.method=='bounds_lower','estimate'].iloc[0]);upper=float(a.loc[a.method=='bounds_upper','estimate'].iloc[0])
        for m in ['complete_y15','ipw_mar','imputed_mnar_odds_1']:
            v=float(a.loc[a.method==m,'estimate'].iloc[0])
            assert lower-1e-8<=v<=upper+1e-8,(m,v,lower,upper)
        assert b['estimate'].is_monotonic_increasing
        assert c['male_code']==1
        assert all(p.name in {x for x in c['aggregate_outputs']} for p in out.iterdir())
        # In particular, outputs contain no IDs or individual microdata rows.
        for fn in out.glob('*'):
            text=fn.read_text()
            assert 'idnum' not in text.lower()
        print('Synthetic regression tests passed. These data are fabricated; NO empirical FFCWS estimate was computed.')

if __name__=='__main__':test()
