"""Locally-generated, fictional data regression test; no participant data."""
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
import pandas as pd
from forensic_histories import run

def main():
    n=300
    d=pd.DataFrame(index=range(n));d['cm1bsex']=1
    d['k6f19']=-9;d.loc[:149,'k6f19']=2
    d['k6f26']=2
    d['k7e58']=1;d['k7e59']=1
    # PRE 30, SAME 40, POST 180, UNDATED 10, NO VAGINAL 20, UNKNOWN 20.
    d['k7e60']=18
    d.loc[:29,'k7e60']=13
    d.loc[30:69,'k7e60']=15
    d.loc[70:249,'k7e60']=18
    d.loc[250:259,'k7e60']=-1
    d.loc[260:279,'k7e59']=2;d.loc[260:279,'k7e60']=-9
    # Skip-coded vaginal NO for the ten respondents who answer any-sex NO.
    d.loc[270:279,'k7e58']=2;d.loc[270:279,'k7e59']=-9
    d.loc[280:299,'k7e59']=-9;d.loc[280:299,'k7e60']=-9
    d['ck6yagem']=15*12+4;d['ck7yagem']=22*12+6
    d['k6natwt']=1.0
    for i in range(1,34):d[f'k6natwt_rep{i}']=1.0
    with TemporaryDirectory() as tmp:
        inp=Path(tmp)/'fictional.csv';out=Path(tmp)/'results'
        d.to_csv(inp,index=False)
        run(inp,out,strict=False)
        q=pd.read_csv(out/'chronology_components.csv').set_index('category')
        assert int(q.loc['reported_age_earlier_than_y15','n_event'])==30
        assert int(q.loc['reported_same_completed_age','n_event'])==40
        assert int(q.loc['reported_age_strictly_after_y15','n_event'])==180
        assert abs(q.loc['reported_age_strictly_after_y15','share']-0.6)<1e-10
        bounds=pd.read_csv(out/'classification_envelope.csv').set_index('scenario')
        assert abs(bounds.loc['confirmed_after_only','share']-0.6)<1e-10
        assert abs(bounds.loc['possible_after_including_missing_adult_outcomes','share']-250/300)<1e-10
        qa=pd.read_csv(out/'routing_quality_checks.csv').set_index('check')
        assert qa.loc['y15_no_explicit_f26_lifetime_no','share']==1
    print('Synthetic forensic tests passed (routing, age-order strata, envelopes, replicate arithmetic).')
if __name__=='__main__':main()
