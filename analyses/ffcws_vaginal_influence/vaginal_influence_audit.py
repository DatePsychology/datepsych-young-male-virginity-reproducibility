#!/usr/bin/env python3
"""Local-only vaginal-specific FFCWS weight influence audit. No microdata exports."""
from __future__ import annotations
import argparse, json, platform, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn
import harmonize_ffcws as h
import ffcws_attrition_reference as ref
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

VERSION = '1.0.0'
NREP = 33
HISTORICAL_PREDICTORS = {'cm1age','cm1ethrace','cm1edu','cm1relf','cm1povca'}
# Quantiles are unweighted across positive-weight observed cases; ties at threshold retained.
SPECS = {
 'cc_original': ('cc_original', 'Unadjusted Year-15 survey weights'),
 'cc_survey_cap_p99': ('cc_original', 'Cap original survey weights at p99'),
 'cc_survey_cap_p95': ('cc_original', 'Cap original survey weights at p95'),
 'ipw_original': ('ipw_original', 'Original survey weight / clipped response probability'),
 'ipw_combined_cap_p99': ('ipw_original', 'Cap combined weights at p99'),
 'ipw_combined_cap_p95': ('ipw_original', 'Cap combined weights at p95'),
 'ipw_response_cap_p99': ('ipw_original', 'Cap inverse response factors at p99 only'),
 'ipw_response_cap_p95': ('ipw_original', 'Cap inverse response factors at p95 only'),
 'ipw_survey_cap_p99': ('ipw_original', 'Cap original survey weights at p99 only, keep original response fit'),
 'ipw_survey_cap_p95': ('ipw_original', 'Cap original survey weights at p95 only, keep original response fit'),
 'ipw_drop_top_p99': ('ipw_original', 'Exclude combined weights strictly above p99'),
 'ipw_drop_top_p95': ('ipw_original', 'Exclude combined weights strictly above p95'),
}

def mean(y, w):
    y, w = np.asarray(y, float), np.asarray(w, float)
    ok = np.isfinite(y) & np.isfinite(w) & (w > 0)
    if not ok.any(): raise ValueError('Empty positive-weight observed denominator')
    return float(np.dot(y[ok], w[ok]) / w[ok].sum())

def cap(w, p):
    return np.minimum(w, np.quantile(w, p, method='linear'))

def fit_response(X, response, w):
    """Same specification as ref.fit_prob; fail on convergence warnings rather than ignore."""
    ok = np.isfinite(w) & (w > 0)
    r = response[ok].astype(int)
    if len(r) < 30 or np.unique(r).size != 2:
        raise ValueError('Replicate has insufficient response variation')
    model = make_pipeline(StandardScaler(), LogisticRegression(C=1., solver='lbfgs', max_iter=1200))
    with warnings.catch_warnings():
        warnings.simplefilter('error', ConvergenceWarning)
        model.fit(X[ok], r, logisticregression__sample_weight=w[ok]/w[ok].mean())
    raw = model.predict_proba(X)[:,1]
    if not np.isfinite(raw).all(): raise ValueError('Nonfinite response predictions')
    return np.clip(raw, .02, .98)

def weights_for_specs(w, multiplier):
    raw = w * multiplier
    result = {'cc_original':w, 'ipw_original':raw}
    for suffix,p in [('p99',.99),('p95',.95)]:
        result['cc_survey_cap_'+suffix] = cap(w,p)
        result['ipw_combined_cap_'+suffix] = cap(raw,p)
        result['ipw_response_cap_'+suffix] = w*cap(multiplier,p)
        result['ipw_survey_cap_'+suffix] = cap(w,p)*multiplier
        result['ipw_drop_top_'+suffix] = np.where(raw>np.quantile(raw,p,method='linear'),0.,raw)
    return result

def concentration(w):
    w = np.asarray(w,float); w = w[w>0]
    if not len(w): raise ValueError('Empty weight vector')
    s = np.sort(w)[::-1]
    return dict(kish_ess=float(w.sum()**2/np.dot(w,w)),
                top_1pct_weight_share_pct=float(100*s[:int(np.ceil(.01*len(s)))].sum()/s.sum()),
                top_5pct_weight_share_pct=float(100*s[:int(np.ceil(.05*len(s)))].sum()/s.sum()))

def evaluate(y,w,X,diag=False):
    response = np.isfinite(y)
    obs = response & (w>0)
    if np.sum(obs)<30 or np.sum(obs&(y==1))<10 or np.sum(obs&(y==0))<10:
        raise ValueError('Insufficient observed outcome counts')
    pi = fit_response(X,response,w)
    weights = weights_for_specs(w[obs],1/pi[obs])
    estimates={}; diagnostics={}
    for name, eff in weights.items():
        keep=eff>0
        if np.sum(keep & (y[obs]==1))<10 or np.sum(keep & (y[obs]==0))<10:
            raise ValueError('Insufficient outcome counts after influence restriction')
        estimates[name]=mean(y[obs],eff)
        # Do not export any dropped-subset outcome, weight total, individual weights or predictions.
        if diag and name in ('cc_original','ipw_original'):
            diagnostics[name]=concentration(eff)
    return estimates,diagnostics

def jk(est, reps):
    a=np.asarray(reps,float)
    if a.shape!=(NREP,) or not np.isfinite(a).all(): raise ValueError('Expected all 33 valid replicates')
    return float(np.sqrt(np.sum((a-est)**2)))

def ci(est,se,prop=False):
    lo,hi=est-1.96*se,est+1.96*se
    return (max(0,lo),min(1,hi)) if prop else (lo,hi)

def strict_validate(n, observed, yes, y22_n, cc, ipw, y22):
    # Published point estimates rounded to two decimal percentage points. Allow 0.02 pp
    # for numerical/library variation, not substantial changes in the analysis.
    checks={'target_n_938':n==938,'observed_n_697':observed==697,'yes_n_514':yes==514,
            'year22_observed_n_697':y22_n==697,
            'cc_matches_75_30_pct':abs(cc-.7530032715)<=.0002,
            'ipw_matches_74_96_pct':abs(ipw-.7496004898)<=.0002,
            'year22_matches_74_26_pct':abs(y22-.7426491729)<=.0002}
    if not all(checks.values()):
        raise ValueError('Historical validation failed: '+', '.join(k for k,v in checks.items() if not v)+
                         '. Check release, outcome coding and library versions; no results written.')
    return checks

def run(source, out, strict=True):
    source,out=Path(source).resolve(),Path(out).resolve()
    if out==source.parent: raise ValueError('Choose an output directory separate from microdata')
    if out.exists() and any(out.iterdir()): raise ValueError('Output directory must be empty or new; avoid stale results')
    d=h.read_restricted(source)
    if len(d)<1000: raise ValueError('Expected all-wave input; too few rows')
    missing=sorted(HISTORICAL_PREDICTORS-set(d.columns))
    if strict and missing: raise ValueError('Missing original model predictors: '+', '.join(missing))
    st=h.code_outcomes(d); vaginal=st['vaginal']
    w6=ref.valid_weight(d['k6natwt']); w7=ref.valid_weight(d['k7natwt'])
    r6=np.array([ref.valid_weight(d[k]) for k in h.REPS6]); r7=np.array([ref.valid_weight(d[k]) for k in h.REPS7])
    target=st['male']&(st['teen']==0)&(w6>0)
    target7=st['male']&(st['teen']==0)&(w7>0)
    X,names,used=ref.covariate_matrix(d)
    if strict and set(used)!=HISTORICAL_PREDICTORS:
        raise ValueError('Response model predictors differ from the historical five; review data release')
    y=vaginal[target]; w=w6[target]; x=X[target]; reps=r6[:,target]
    observed=int(np.isfinite(y).sum()); yes=int((y==1).sum())
    y22_n=int((target7&np.isfinite(vaginal)).sum())
    if strict and (target.sum()!=938 or observed!=697 or yes!=514):
        raise ValueError('Historical sample counts differ (expected 938 / 697 / 514); no results written')
    full,diag=evaluate(y,w,x,diag=True)
    # Independently compare original baseline with the unchanged harmonization helpers.
    cc_ref=h.survey_stats(vaginal,target,w6,r6)
    ipw_ref=h.ipw_stats(vaginal,target,w6,r6,X)
    y22_ref=h.survey_stats(vaginal,target7,w7,r7)
    y22=y22_ref['estimate']
    if abs(full['cc_original']-cc_ref['estimate'])>1e-10 or abs(full['ipw_original']-ipw_ref['estimate'])>1e-10:
        raise ValueError('Baseline differs from archived reference estimator')
    checks=strict_validate(int(target.sum()),observed,yes,y22_n,full['cc_original'],full['ipw_original'],y22) if strict else {}
    if strict:
        checks.update({'cc_historical_se':abs(cc_ref['se']-.03782712358)<=.0002,
                       'ipw_historical_se':abs(ipw_ref['se']-.03561092319)<=.0002,
                       'year22_historical_se':abs(y22_ref['se']-.03967840036)<=.0002,
                       'year22_eligible_n_734':int(target7.sum())==734,
                       'input_n_4898':len(d)==4898})
        if not all(checks.values()): raise ValueError('Historical variance or frame mismatch: '+', '.join(k for k,v in checks.items() if not v))
    print('Baseline validation passed.' if strict else 'Synthetic/nonhistorical mode: no historical validation.',flush=True)
    rep_rows=[]
    for j,ww in enumerate(reps,1):
        a,_=evaluate(y,ww,x)
        rep_rows.append(a)
        if j%5==0 or j==NREP: print(f'Completed {j}/{NREP} jackknife replicates',flush=True)
    rep={k:np.array([row[k] for row in rep_rows]) for k in SPECS}
    for k,old in [('cc_original',cc_ref),('ipw_original',ipw_ref)]:
        if abs(jk(full[k],rep[k])-old['se'])>1e-10: raise ValueError('Replicate SE differs from archived reference')
    rows=[]
    for name,(base,note) in SPECS.items():
        est=full[name]; se=jk(est,rep[name]); lo,hi=ci(est,se,True)
        delta=est-full[base]; dse=jk(delta,rep[name]-rep[base]); dl,dh=ci(delta,dse)
        dc=est-full['cc_original']; dcse=jk(dc,rep[name]-rep['cc_original']); dcl,dch=ci(dc,dcse)
        rows.append(dict(specification=name,comparison_baseline=base,estimate_pct=100*est,se_pp=100*se,
                         ci95_low_pct=100*lo,ci95_high_pct=100*hi,delta_vs_baseline_pp=100*delta,
                         delta_ci95_low_pp=100*dl,delta_ci95_high_pp=100*dh,
                         delta_vs_cc_pp=100*dc,delta_vs_cc_ci95_low_pp=100*dcl,delta_vs_cc_ci95_high_pp=100*dch,
                         replicates_valid=NREP,description=note))
    rows.append(dict(specification='year22_original_cc',comparison_baseline='not_paired_different_weight_frame',
                     estimate_pct=100*y22,se_pp=100*y22_ref['se'],ci95_low_pct=100*y22_ref['ci_low'],
                     ci95_high_pct=100*y22_ref['ci_high'],replicates_valid=NREP,
                     description='Year-22 weighted observed cases; not paired with Year-15 replicates'))
    # All files are aggregate-only. Round exported statistics to 2 decimal percentage points.
    meta=dict(version=VERSION, historical_strict_mode=strict, historical_checks=checks,
              input_record_count=int(len(d)), target_n=int(target.sum()), observed_n=observed, positive_n=yes,
              year22_observed_n=y22_n, predictor_variables=used, predictor_columns=len(names),
              response_definition='finite harmonized Year-22 vaginal outcome',
              weight_replicates=NREP, variance='sum squared deviations from full sample; paired differences use same replicates',
              propensity_model='normalized-weight L2 logistic C=1, StandardScaler, probability clip 0.02–0.98; refit per replicate',
              cap_rule='unweighted linear quantile of positive-weight observed cases, recalculated within each replicate; delete strictly above cutoff',
              data_scope='original Year-15 positive national-weight male adolescent lifetime-no domain; Year-22 separate sensitivity frame',
              independent_reference_checks='archived CC and IPW point estimates and replicate SEs agree',
              software=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__),
              limitations='Sensitivity diagnostics, not corrected population estimates. Does not resolve MNAR, reporting errors, or cohort transport. Wald intervals, adaptive thresholds are exploratory. No per-replicate or per-person results exported.')
    out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(out/'vaginal_weight_sensitivity.csv',index=False,float_format='%.2f')
    pd.DataFrame([dict(specification=k,**v) for k,v in diag.items()]).to_csv(out/'vaginal_weight_concentration.csv',index=False,float_format='%.2f')
    (out/'audit_validation.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    print('Success. Aggregate-only results saved to:',out)
    return rows,meta

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--allwaves',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--synthetic-test-mode',action='store_true',help='Disable historical checks ONLY for artificial fixtures; never use to bypass a real-data mismatch')
    a=p.parse_args(); run(a.allwaves,a.out,not a.synthetic_test_mode)
