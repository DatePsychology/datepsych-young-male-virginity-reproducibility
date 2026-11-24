"""Run synthetic tests without FFCWS respondent data. All synthetic records are fabricated."""
import argparse
from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
from harmonize_ffcws import code_outcomes, survey_stats, run, REPS6, REPS7


def test_routing():
    d=pd.DataFrame(dict(cm1bsex=[1]*7,
        k6f19=[-6,1,-6,-6,-6,2,2],
        k6f26=[2,-6,2,2,2,1,-3],
        k7e58=[2,1,1,1,2,1,1],
        k7e59=[-6,1,2,-3,1,1,1],
        k7e60=[-6,17,-6,-3,12,15,22],
        ck6yagem=[182]*7,ck7yagem=[265]*7))
    z=code_outcomes(d)
    assert np.allclose(z['teen'][:5],[0,1,0,0,0])
    assert z['vaginal'][0]==0, 'skip on no sex must imply no vaginal sex'
    assert z['vaginal'][1]==1 and z['vaginal'][2]==0
    assert np.isnan(z['vaginal'][3]), 'refused vaginal question must remain unknown'
    assert np.isnan(z['vaginal'][4]) and np.isnan(z['anysex'][4]), 'logical contradictions must remain unknown'
    assert z['male'].sum()==7
    # Direct statistical uncertainty check for constant outcomes.
    testy=np.ones(12);testw=np.ones(12)
    reps=np.ones((33,12));s=survey_stats(testy,np.ones(12,bool),testw,reps)
    assert abs(s['estimate']-1.)<1e-10 and s['se']<1e-10


def test_workflow():
    rng=np.random.default_rng(20261124)
    n=1200
    d=pd.DataFrame({
        'cm1bsex':rng.choice([1,2],n,p=[.52,.48]),
        'k6f19':np.full(n,-6),
        'k6f26':rng.choice([1,2],n,p=[.2,.8]),
        'k7e58':rng.choice([1,2,-3],n,p=[.73,.2,.07]),
        'ck6yagem':rng.choice([177,185,190,194,199],n),
        'ck7yagem':rng.choice([250,259,267,271,279,283],n),
        'k6natwt':rng.uniform(.5,2,n),
        'k7natwt':rng.uniform(.5,2,n),
    })
    e=np.where(d.k7e58.to_numpy()==1,
        rng.choice([1,2,-3],n,p=[.86,.11,.03]),-6)
    d['k7e59']=e
    d['k7e60']=np.where(e==1,rng.choice([15,16,18,19,20,21,22,23],n),-6)
    for i in range(1,34):
        fac=1.+0.01*np.sin((np.arange(n)+i)*.11)
        d[f'k6natwt_rep{i}']=d['k6natwt'].to_numpy()*fac
        d[f'k7natwt_rep{i}']=d['k7natwt'].to_numpy()*fac
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp)
        d.to_csv(p/'synthetic.csv',index=False)
        run(argparse.Namespace(allwaves=str(p/'synthetic.csv'),out=str(p/'results'),strict=False))
        for f in ['harmonized_outcomes.csv','matched_outcome_gap.csv',
                  'birthday_milestones.csv','routing_and_quality_audit.csv','SUMMARY.md']:
            assert (p/'results'/f).exists(),f
        core=pd.read_csv(p/'results'/'harmonized_outcomes.csv')
        a=core[(core.measure=='any_sex_matched')&(core.domain=='year15')&(core.estimator=='complete_case')].iloc[0]
        v=core[(core.measure=='vaginal_matched')&(core.domain=='year15')&(core.estimator=='complete_case')].iloc[0]
        gap=core[(core.measure=='sex_without_vaginal_matched')&(core.domain=='year15')&(core.estimator=='complete_case')].iloc[0]
        assert abs(a.estimate-v.estimate-gap.estimate)<1e-10
        assert a.n_observed==v.n_observed==gap.n_observed
        born=pd.read_csv(p/'results'/'birthday_milestones.csv')
        for cut in born.cutoff_birthday.unique():
            b=born[born.cutoff_birthday==cut].set_index('scenario')
            if not np.isnan(b.loc['complete_cases','estimate']):
                assert b.loc['missing_debut_all_no','estimate']<=b.loc['complete_cases','estimate']+1e-8
                assert b.loc['missing_debut_all_yes','estimate']>=b.loc['complete_cases','estimate']-1e-8

if __name__=='__main__':
    test_routing(); test_workflow()
    print('Synthetic harmonization tests passed: routing, paired gaps, birthday eligibility, full aggregate output.')
