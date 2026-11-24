"""Fabricated data only: arithmetic, routing, uncertainty and full local pipeline."""
from pathlib import Path
import tempfile
import json
import numpy as np
import pandas as pd
import vaginal_influence_audit as a
from test_harmonize_synthetic import test_routing

def test_arithmetic():
    w=np.array([1.,2.,3.,4.,100.]); m=np.array([1.,1.,1.,2.,3.]); y=np.array([1.,1.,0.,1.,0.])
    z=a.weights_for_specs(w,m)
    assert abs(a.mean(y,z['cc_original'])-7/110)<1e-12
    assert abs(a.mean(y,z['ipw_original'])-11/314)<1e-12
    assert abs(a.mean(y,z['ipw_drop_top_p99'])-11/14)<1e-12
    assert np.allclose(z['ipw_response_cap_p95'],w*np.minimum(m,2.8))
    assert np.allclose(z['ipw_survey_cap_p95'],np.minimum(w,80.8)*m)
    assert a.concentration(np.ones(100))['kish_ess']==100
    assert a.concentration(np.ones(100))['top_1pct_weight_share_pct']==1
    r1=np.linspace(.3,.7,33); r2=r1+.1
    assert a.jk(.1,r2-r1)<1e-14
    assert abs(a.jk(.5,np.r_[.6,np.full(32,.5)])-.1)<1e-12
    assert all(a.strict_validate(938,697,514,697,.7530032715,.7496004898,.7426491729).values())
    try: a.strict_validate(938,696,514,697,.753,.7496,.7426)
    except ValueError: pass
    else: raise AssertionError('Mismatched real baseline accepted')

def fixture():
    rng=np.random.default_rng(20261124);n=1800
    d=pd.DataFrame(dict(cm1bsex=rng.choice([1,2],n),k6f19=np.full(n,-6),
        k6f26=rng.choice([1,2],n,p=[.15,.85]),k7e58=rng.choice([1,2,-3],n,p=[.65,.15,.2]),
        ck6yagem=rng.choice([177,185,190,194,199],n),ck7yagem=rng.choice([250,259,267,271,279,283],n),
        k6natwt=np.exp(rng.normal(0,1,n)),k7natwt=np.exp(rng.normal(0,1,n)),
        cm1age=rng.integers(18,43,n),cm1ethrace=rng.integers(1,5,n),cm1edu=rng.integers(1,5,n),
        cm1relf=rng.integers(1,4,n),cm1povca=rng.integers(1,4,n)))
    d['k7e59']=np.where(d.k7e58==1,rng.choice([1,2,-3],n,p=[.85,.1,.05]),-6)
    d['k7e60']=np.where(d.k7e59==1,18,-6)
    groups=rng.integers(0,33,n)
    for j in range(1,34):
        factor=np.where(groups==j-1,0.,33/32)
        d[f'k6natwt_rep{j}']=d.k6natwt*factor
        d[f'k7natwt_rep{j}']=d.k7natwt*factor
    return d

def test_pipeline():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp); d=fixture(); source=root/'synthetic.dta';d.to_stata(source,write_index=False,version=118)
        rows,meta=a.run(source,root/'results',strict=False)
        assert meta['weight_replicates']==33 and meta['historical_strict_mode'] is False
        s=pd.read_csv(root/'results'/'vaginal_weight_sensitivity.csv').set_index('specification')
        assert len(s)==13 and (s.replicates_valid==33).all()
        assert (s.estimate_pct.between(0,100)).all()
        assert (s.ci95_low_pct<=s.estimate_pct).all() and (s.ci95_high_pct>=s.estimate_pct).all()
        for base in ('cc_original','ipw_original'):
            assert s.loc[base,'delta_vs_baseline_pp']==0
            assert s.loc[base,'delta_ci95_low_pp']==0 and s.loc[base,'delta_ci95_high_pp']==0
        for k,r in s.iterrows():
            if k!='year22_original_cc':
                assert abs(r.delta_vs_baseline_pp-(r.estimate_pct-s.loc[r.comparison_baseline,'estimate_pct']))<=.011
        assert {p.name for p in (root/'results').iterdir()}=={'vaginal_weight_sensitivity.csv','vaginal_weight_concentration.csv','audit_validation.json'}
        try: a.run(source,root/'invalid_strict',strict=True)
        except ValueError: assert not (root/'invalid_strict').exists()
        else: raise AssertionError('Synthetic data accepted as historical data')
        try: a.run(source,root/'results',strict=False)
        except ValueError: pass
        else: raise AssertionError('Nonempty output directory accepted')
        # Verify CSV ingestion also agrees with Stata ingestion on the same fabricated rows.
        csv=root/'synthetic.csv';d.to_csv(csv,index=False)
        rows2,_=a.run(csv,root/'csv_results',strict=False)
        assert np.allclose([r['estimate_pct'] for r in rows],[r['estimate_pct'] for r in rows2],atol=1e-9)
if __name__=='__main__':
    test_routing();test_arithmetic();test_pipeline()
    print('PASS: routing, exact weight arithmetic, paired jackknife, historical rejection, Stata and CSV pipeline, aggregate outputs.')
