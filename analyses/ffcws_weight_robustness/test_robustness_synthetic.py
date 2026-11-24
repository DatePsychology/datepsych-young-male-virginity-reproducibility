"""Synthetic tests: no actual FFCWS microdata used."""
from __future__ import annotations
import tempfile, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd

def main():
    rng=np.random.default_rng(20261124)
    n=680
    d=pd.DataFrame(index=range(n))
    d['cm1bsex']=rng.choice([1,2],n,p=[.8,.2])
    d['k6f19']=np.full(n,-6)
    d['k6f26']=rng.choice([1,2,-1],n,p=[.22,.72,.06]);
    d['k6natwt']=rng.lognormal(0,1,n)*rng.choice([0,1],n,p=[.15,.85])
    d['k7natwt']=d['k6natwt'].to_numpy()*rng.uniform(.75,1.25,n)
    d['cm1age']=rng.integers(17,47,n)
    d['cm1ethrace']=rng.choice([1,2,3,4],n,p=[.35,.2,.3,.15])
    d['cm1edu']=rng.choice([1,2,3,4],n)
    d['cm1relf']=rng.choice([1,2,3,4],n)
    d['cm1povca']=rng.choice([1,2,3,4,5],n)
    d['ck6childageinterviewm']=rng.integers(175,205,n)
    for v in ['k6d40','k6d48','k6f63','k6d2b','k6d61c']:
        d[v]=rng.choice([1,2,-6],n,p=[.3,.65,.05])
    signal=.2*(d['cm1ethrace'].to_numpy()==1)-.3*(d['cm1povca'].to_numpy()==5)
    pr=1/(1+np.exp(-(.8+signal)))
    response=rng.binomial(1,pr)
    outcome=rng.binomial(1,np.clip(.72+.06*(d['cm1ethrace'].to_numpy()==2),.1,.9))
    d['k7e58']=np.where(response==1, np.where(outcome==1,1,2),-1)
    d['k7e59']=d['k7e58']
    for i in range(1,34):
        factor=rng.uniform(.8,1.2,n)
        d[f'k6natwt_rep{i}']=d['k6natwt']*factor
        d[f'k7natwt_rep{i}']=d['k7natwt']*factor
    with tempfile.TemporaryDirectory() as t:
        t=Path(t);d.to_csv(t/'synthetic.csv',index=False)
        proc=subprocess.run([sys.executable,'robustness_audit.py','--allwaves',str(t/'synthetic.csv'),'--out',str(t/'results')],capture_output=True,text=True,timeout=180)
        if proc.returncode:
            print(proc.stdout);print(proc.stderr);raise RuntimeError('Synthetic audit failure')
        r=pd.read_csv(t/'results'/'model_variants.csv')
        s=pd.read_csv(t/'results'/'independent_solver_check.csv')
        b=pd.read_csv(t/'results'/'original_frame_bounds.csv')
        assert len(r)==13 and len(s)==4
        assert all((r.estimate>0)&(r.estimate<1))
        assert float(b.iloc[0].rate)<=float(r.iloc[0].estimate)<=float(b.iloc[1].rate)
        assert abs(float(s.iloc[0].point)-float(s.iloc[1].point))<.003, s
        assert abs(float(s.iloc[0].se)-float(s.iloc[1].se))<.003, s
        print('Synthetic regression tests passed (13 variants, independent optimizer, two sharp bounds).')

if __name__=='__main__': main()
