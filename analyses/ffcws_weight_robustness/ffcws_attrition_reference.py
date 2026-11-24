#!/usr/bin/env python3
"""FFCWS sex-initiation transition: local-only selection/attrition sensitivity.

No respondent records, IDs, row-level predictions, or microdata are exported.
Outputs: aggregate CSV/JSON only. See README.md before use.

Python >=3.10; numpy, pandas, scikit-learn.
"""
from __future__ import annotations
import argparse, hashlib, json, math, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.exceptions import ConvergenceWarning

REPN = 33
R6 = [f'k6natwt_rep{i}' for i in range(1, REPN+1)]
R7 = [f'k7natwt_rep{i}' for i in range(1, REPN+1)]
BASE_CATS = ['cm1ethrace', 'cm1edu', 'cm1relf', 'cm1povca']
BASE_CONT = {'cm1age': (13,60), 'ck6childageinterviewm': (150,260)}
MUST_HAVE = ['cm1bsex','k6f19','k6f26','k7e58','k7e59','k6natwt','k7natwt']
OPTIONAL = BASE_CATS + list(BASE_CONT) + R6 + R7
OUTPUTS = ['sample_flow.csv','sample_comparisons.csv','baseline_balance.csv',
           'estimates.csv','mnar_sensitivity.csv','tipping_points.csv',
           'weight_diagnostics.csv','audit_summary.json']


def numeric(d, name):
    if name not in d.columns:
        return pd.Series(np.nan, index=d.index, dtype=float)
    return pd.to_numeric(d[name],errors='coerce')


def load_data(filename):
    filename=Path(filename)
    names = {x.lower() for x in MUST_HAVE+OPTIONAL}
    if filename.suffix.lower()=='.dta':
        with pd.io.stata.StataReader(str(filename)) as reader:
            available = list(reader.variable_labels().keys())
        selected = [s for s in available if s.lower() in names]
        d=pd.read_stata(filename, columns=selected, convert_categoricals=False,
                        convert_missing=False)
    elif filename.suffix.lower()=='.csv':
        d=pd.read_csv(filename, usecols=lambda c:c.lower() in names,low_memory=False)
    else:
        raise ValueError('Expected a .dta or .csv file.')
    d.columns=d.columns.str.lower()
    if d.columns.duplicated().any():
        raise ValueError('Duplicate variable names after case normalizing.')
    missing=[x for x in MUST_HAVE if x not in d.columns]
    if missing:
        raise ValueError('Missing required columns: '+', '.join(missing))
    return d


def classify(d, male_code):
    sex=numeric(d,'cm1bsex')
    a=numeric(d,'k6f19')
    b=numeric(d,'k6f26')
    early=pd.Series(np.nan,index=d.index,dtype=float)
    early[a.eq(1) | b.eq(1)]=1.0
    early[b.eq(2) & ~a.eq(1)]=0.0
    yy=numeric(d,'k7e58')
    adult=pd.Series(np.nan,index=d.index,dtype=float)
    adult[yy.eq(1)]=1.0;adult[yy.eq(2)]=0.0
    return sex.eq(male_code).to_numpy(bool),early.to_numpy(float),adult.to_numpy(float)


def valid_weight(s):
    w=pd.to_numeric(s,errors='coerce').to_numpy(float)
    return np.where(np.isfinite(w)&(w>0),w,0.)


def wmean(v,w):
    v=np.asarray(v,float);w=np.asarray(w,float)
    okay=np.isfinite(v)&np.isfinite(w)&(w>0)
    if not okay.any() or w[okay].sum()<=0:return float('nan')
    return float(np.dot(v[okay],w[okay])/w[okay].sum())


def effective_n(w):
    w=np.asarray(w,float)
    w=w[np.isfinite(w)&(w>0)]
    if not len(w):return float('nan')
    return float(w.sum()**2 / np.dot(w,w))


def as_record(name, est, n, replicate_estimates=None, note=''):
    arr=np.asarray(replicate_estimates if replicate_estimates is not None else [],float)
    arr=arr[np.isfinite(arr)]
    # FFCWS random-group replicate weights: MSE centering, multiplier 1.
    se=math.sqrt(float(np.sum((arr-est)**2))) if len(arr)==REPN and np.isfinite(est) else float('nan')
    return dict(method=name,n=int(n),estimate=float(est),se_replicate=se,
       ci_low=max(0.,est-1.96*se) if np.isfinite(se) else None,
       ci_high=min(1.,est+1.96*se) if np.isfinite(se) else None,
       usable_replicates=int(len(arr)),note=note)


def covariate_matrix(df):
    """Prespecified pre-followup predictors; codes are not interpreted as outcomes."""
    mats=[];info=[];used=[]
    for var,(lo,hi) in BASE_CONT.items():
        if var not in df.columns:continue
        vals=pd.to_numeric(df[var],errors='coerce').to_numpy(float)
        valid=np.isfinite(vals)&(vals>=lo)&(vals<=hi)
        if valid.sum()<30:continue
        med=float(np.median(vals[valid]))
        sd=float(np.std(vals[valid])) or 1.
        x=np.where(valid,vals,med)
        mats.append(((x-med)/sd)[:,None]);info.append(var+':continuous')
        if (~valid).any():mats.append((~valid).astype(float)[:,None]);info.append(var+':missing')
        used.append(var)
    for var in BASE_CATS:
        if var not in df.columns:continue
        z=pd.to_numeric(df[var],errors='coerce')
        vals=[]
        for v in z:
            if pd.isna(v) or (not np.isfinite(v)) or float(v)<0:
                vals.append('missing')
            else:
                vals.append(str(int(v)) if float(v).is_integer() else str(round(float(v),4)))
        z2=pd.Series(vals)
        if z2.nunique()==1:continue
        freq=z2.value_counts()
        allowed=set(freq[freq>=15].index)
        z2=z2.map(lambda x:x if x in allowed else 'other')
        dum=pd.get_dummies(z2,prefix=var,drop_first=True).astype(float)
        if dum.shape[1]>12:
            raise ValueError(f'Unexpectedly many categories for {var}; inspect its data dictionary.')
        if not dum.empty:mats.append(dum.to_numpy());info.extend(list(dum.columns));used.append(var)
    if not mats:
        return np.ones((len(df),1),float),['intercept_only'],used
    return np.concatenate(mats,axis=1),info,used


def fit_prob(x,y,w,clamp=(0.02,0.98)):
    y=np.asarray(y,float);w=np.asarray(w,float)
    ok=np.isfinite(y)&np.isfinite(w)&(w>0)
    if not ok.any():raise ValueError('No observations for model')
    p=wmean(y[ok],w[ok]);
    if len(set(y[ok].astype(int)))<2:return np.full(len(x),np.clip(p,*clamp))
    # Normalize weights so the regularization strength is sample-size invariant.
    ww=w[ok]/np.mean(w[ok]);
    model=make_pipeline(StandardScaler(),LogisticRegression(C=1.,solver='lbfgs',max_iter=1200))
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',ConvergenceWarning)
        model.fit(x[ok],y[ok].astype(int),logisticregression__sample_weight=ww)
    return np.clip(model.predict_proba(x)[:,1],*clamp)


def estimate_scenarios(y,elig,w,X,odds,prop_clip):
    """Calculate on age-15 national-weight frame, one sex/initiation subgroup."""
    idx=np.flatnonzero(elig)
    if len(idx)<20:raise ValueError('Too few eligible male age15 noninitiators with national weights.')
    y=y[idx]; wt=w[idx];xx=X[idx]
    obs=np.isfinite(y)
    if obs.sum()<20 or (~obs).sum()<1:raise ValueError('Missing outcomes or too few observed responses.')
    obs_prob=fit_prob(xx,obs.astype(float),wt,clamp=prop_clip)
    mu_all=fit_outcome_predict(xx, y, obs, wt)
    direct=wmean(y[obs],wt[obs]);
    ipw=wmean(y[obs],wt[obs]/obs_prob[obs]);
    full=wmean(np.where(obs,y,0.),wt)
    obs_weight=float(wt[obs].sum()/wt.sum())
    low=full
    high=full+1.-obs_weight
    aipw=float(np.dot(wt,mu_all+np.where(obs,(np.nan_to_num(y, nan=0.)-mu_all)/obs_prob,0.))/wt.sum())
    imps={}
    logit=np.log(mu_all/(1-mu_all))
    for mult in odds:
        pp=1./(1.+np.exp(-(logit+np.log(mult))))
        imps[mult]=float(np.dot(wt, np.where(obs,np.nan_to_num(y,nan=0.),pp))/wt.sum())
    return {'complete_y15':direct,'ipw_mar':ipw,'aipw_mar':aipw,
           'bounds_lower':low,'bounds_upper':high,'mnar':imps,
           'obs_weight_frac':obs_weight,'obs_rate_unweighted':float(obs.mean()),
           'n_eligible':int(len(idx)),'n_observed':int(obs.sum()),
           'ess_complete':effective_n(wt[obs]),
           'ess_ipw':effective_n(wt[obs]/obs_prob[obs]),
           'prop_min':float(obs_prob.min()),'prop_p05':float(np.quantile(obs_prob,.05)),
           'prop_median':float(np.median(obs_prob)),
           'prop_p95':float(np.quantile(obs_prob,.95)),
           'prop_max':float(obs_prob.max()),
           'max_ipw_to_median':float(np.max(wt[obs]/obs_prob[obs])/np.median(wt[obs]/obs_prob[obs])),
           'frac_prop_clip':float(np.mean((obs_prob<=prop_clip[0]+1e-10)|(obs_prob>=prop_clip[1]-1e-10))),
           'missing_required':{z:float((z-obs_weight*direct)/(1-obs_weight)) for z in [.5,2/3,.75,.8]}}


def fit_outcome_predict(X,y,obs,wt):
    yo=np.asarray(y,float)[obs];wo=np.asarray(wt,float)[obs];xx=np.asarray(X,float)
    if len(set(yo.astype(int)))<2:
        return np.full(len(xx),np.clip(wmean(yo,wo),1e-4,1-1e-4))
    model=make_pipeline(StandardScaler(),LogisticRegression(C=1.,solver='lbfgs',max_iter=1200))
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',ConvergenceWarning)
        model.fit(xx[obs],yo.astype(int),logisticregression__sample_weight=wo/wo.mean())
    return np.clip(model.predict_proba(xx)[:,1],1e-4,1-1e-4)


def baseline_balance(d, male, early, y, frame, w, cutoff=15):
    rows=[]
    eligible=frame & male & (early==0)
    observed=eligible & np.isfinite(y)
    missed=eligible & ~np.isfinite(y)
    for v in BASE_CATS:
        if v not in d:continue
        z=pd.to_numeric(d[v],errors='coerce').to_numpy(float)
        values=np.unique(np.where(np.isfinite(z)&(z>=0),z,-999))
        for val in values:
            n_all=int(np.sum(eligible&(np.where(np.isfinite(z)&(z>=0),z,-999)==val)))
            n_obs=int(np.sum(observed&(np.where(np.isfinite(z)&(z>=0),z,-999)==val)))
            n_mis=n_all-n_obs
            if n_all<cutoff or n_obs<cutoff or n_mis<cutoff:continue
            indicator=np.where(np.isfinite(z)&(z>=0),z,-999)==val
            p_obs=wmean(indicator[observed],w[observed]);p_mis=wmean(indicator[missed],w[missed])
            pool=math.sqrt(max(1e-8,(p_obs*(1-p_obs)+p_mis*(1-p_mis))/2))
            rows.append({'variable':v,'category_code': 'missing' if val==-999 else str(int(val)),
                         'n_observed':n_obs,'n_missing':n_mis,'pct_observed_group':100*p_obs,
                         'pct_missing_group':100*p_mis,'std_difference':(p_obs-p_mis)/pool})
    for v,limits in BASE_CONT.items():
        if v not in d:continue
        z=pd.to_numeric(d[v],errors='coerce').to_numpy(float)
        valid=np.isfinite(z)&(z>=limits[0])&(z<=limits[1])
        both=eligible&valid
        oo=both&np.isfinite(y);mm=both&~np.isfinite(y)
        if oo.sum()<cutoff or mm.sum()<cutoff:continue
        av=wmean(z[oo],w[oo]);bv=wmean(z[mm],w[mm])
        variance=(np.average((z[oo]-av)**2,weights=w[oo])+np.average((z[mm]-bv)**2,weights=w[mm]))/2
        rows.append({'variable':v,'category_code':'weighted_mean',
                   'n_observed':int(oo.sum()),'n_missing':int(mm.sum()),
                   'pct_observed_group':av,'pct_missing_group':bv,
                   'std_difference':(av-bv)/math.sqrt(max(variance,1e-8))})
    return rows


def run(args):
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    p=Path(args.allwaves).resolve()
    if out==p.parent:raise ValueError('Set --out to a separate output directory')
    d=load_data(p)
    male,early,adult=classify(d,args.male_code)
    w6=valid_weight(d['k6natwt']);w7=valid_weight(d['k7natwt'])
    re6=[valid_weight(d[x]) for x in R6 if x in d]
    re7=[valid_weight(d[x]) for x in R7 if x in d]
    if len(re6)!=REPN or len(re7)!=REPN:
        raise ValueError(f'Expected 33 Year 15 and 33 Year 22 replicate weights; found {len(re6)}/{len(re7)}. Cannot produce design intervals.')
    y15frame=male & np.isfinite(early) & (w6>0)
    target=y15frame & (early==0)
    observed=target & np.isfinite(adult)
    oldframe=male & (early==0) & np.isfinite(adult) & (w7>0)
    other=male & np.isfinite(early)&(early==1)&(w6>0)
    flows=[
      ('all_male_baseline',male),
      ('male_valid_age15_status',male&np.isfinite(early)),
      ('male_age15_no_all_cities',male&(early==0)),
      ('male_age15_no_early_national_weight',target),
      ('male_age15_no_y22_status_all_cities',male&(early==0)&np.isfinite(adult)),
      ('male_age15_no_y22_status_y15_national',observed),
      ('male_age15_no_y22_status_y22_national',oldframe),
      ('male_age15_yes_early_national_weight',other)
    ]
    pd.DataFrame([{'stage':name,'n':int(mask.sum())} for name,mask in flows]).to_csv(out/'sample_flow.csv',index=False)
    compare=[]
    for label,ff in [('no_intercourse_age15',target),('intercourse_age15',other)]:
        of=ff&np.isfinite(adult)
        compare.append({'year15_group':label,'n_year15_national':int(ff.sum()),
                        'n_year22_status':int(of.sum()),
                        'followup_response_rate_unweighted':float(of.sum()/ff.sum()) if ff.sum() else None,
                        'followup_response_rate_year15_weighted':float(w6[of].sum()/w6[ff].sum()) if ff.any() else None})
    pd.DataFrame(compare).to_csv(out/'sample_comparisons.csv',index=False)
    xb,feat,used=covariate_matrix(d)
    odds=[float(x) for x in args.odds.split(',')]
    if any(x<=0 for x in odds) or 1. not in odds:
        raise ValueError('--odds must include 1 and all values must be >0')
    prop_clip=(args.clip,1.-args.clip)
    if not 0<args.clip<.3:raise ValueError('clip must be in (0,0.3)')
    point=estimate_scenarios(adult,target,w6,xb,odds,prop_clip)
    print('Running replicate-weight model refits (33 replicates)...',flush=True)
    reps=[]
    for i,ww in enumerate(re6):
        trial=estimate_scenarios(adult,target,ww,xb,odds,prop_clip)
        reps.append(trial)
        if (i+1)%11==0:print(f'  {i+1}/33',flush=True)
    rows=[]
    for method in ['complete_y15','ipw_mar','aipw_mar','bounds_lower','bounds_upper']:
        rows.append(as_record(method,point[method],point['n_observed'] if method in ['complete_y15','ipw_mar'] else point['n_eligible'],
                              [r[method] for r in reps], 'Year15 national frame; replicate model refits; CI reflects design, not identification of missing outcomes'))
    for z in odds:
        rows.append(as_record(f'imputed_mnar_odds_{z:g}',point['mnar'][z],point['n_eligible'],
                  [r['mnar'][z] for r in reps], 'Assumed odds multiplier among unobserved vs conditionally modeled respondents'))
    original=wmean(adult[oldframe],w7[oldframe])
    origreps=[wmean(adult[oldframe],rr[oldframe]) for rr in re7]
    rows.append(as_record('original_y22_national_complete_case',original,int(oldframe.sum()),origreps,
                          'Replicates Year22-weighted 80.07% historical result; different weight domain'))
    allcity=male & (early==0)&np.isfinite(adult)
    rows.append(as_record('unweighted_allcity_observed',float(np.mean(adult[allcity])) if allcity.any() else float('nan'),int(allcity.sum()),
                    None,'Unweighted 20-city convenience comparison; not population representative'))
    pd.DataFrame(rows).to_csv(out/'estimates.csv',index=False,float_format='%.8g')
    pd.DataFrame([{'missing_outcome_odds_ratio':z,'estimate':point['mnar'][z],
            'ci_low':next(q for q in rows if q['method']==f'imputed_mnar_odds_{z:g}')['ci_low'],
            'ci_high':next(q for q in rows if q['method']==f'imputed_mnar_odds_{z:g}')['ci_high']}
            for z in odds]).to_csv(out/'mnar_sensitivity.csv',index=False)
    tipping=[]
    for targetrate,q in point['missing_required'].items():
        tipping.append({'target_total_initiation_rate':targetrate,'required_missing_initiation_rate':q,
                        'feasible_between_0_and_1':bool(0<=q<=1),
                        'observed_outcome_rate_year15_weighted':point['complete_y15'],
                        'weighted_followup_observation_fraction':point['obs_weight_frac']})
    pd.DataFrame(tipping).to_csv(out/'tipping_points.csv',index=False)
    pd.DataFrame([{'metric':k,'value':point[k]} for k in ['obs_rate_unweighted','obs_weight_frac',
                      'ess_complete','ess_ipw','prop_min','prop_p05','prop_median','prop_p95',
                      'prop_max','max_ipw_to_median','frac_prop_clip']]).to_csv(out/'weight_diagnostics.csv',index=False)
    pd.DataFrame(baseline_balance(d,male,early,adult,w6>0,w6,cutoff=args.disclosure_n),
                  columns=['variable','category_code','n_observed','n_missing','pct_observed_group','pct_missing_group','std_difference']).to_csv(out/'baseline_balance.csv',index=False)
    audit={'analysis':'FFCWS Year15->Year22 sexual initiation / selection audit',
          'microdata_exported':False,'aggregate_outputs':OUTPUTS,
          'source_file_sha256':hashlib.sha256(p.read_bytes()).hexdigest() if args.checksum else 'not_calculated_use_--checksum',
          'rows_imported':int(len(d)),'male_code':args.male_code,
          'early_classification':'Original Year15 k6f19/k6f26 routing',
          'outcome':'Year22 k7e58 ever sex (not specifically vaginal intercourse)',
          'national_year15_n_total':int(target.sum()),'national_year15_followup_n':int(observed.sum()),
          'year22_national_original_n':int(oldframe.sum()),
          'allcity_year15_no_total':int(np.sum(male&(early==0))),
          'allcity_year15_no_followup':int(np.sum(allcity)),
          'predictors_used':used,'model_columns':feat,
          'weights_primary':'k6natwt, k6natwt_rep1-33',
          'weights_replication':'k7natwt, k7natwt_rep1-33',
          'variance':'33 supplied random-group replicates, sum(rep-est)^2, model refit (except Year22 historical)',
          'limits':['No inference for boys without Year15 sexual-experience data',
                    'MAR/IPW imputation depends on observed predictors; MNAR assumptions not testable',
                    'Year15 and Year22 national weights may target different response-conditioned populations',
                    'Some model/refit variance is approximate and not externally cross-validated',
                    'Births in large US cities 1998-2000; no generalization to modern youth without caveat']}
    (out/'audit_summary.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
    print('Outputs (all aggregate; no respondent data):')
    for fn in OUTPUTS:print(' ',out/fn)
    print('Primary Year22 complete-case:',round(original,4),'Year15 IPW:',round(point['ipw_mar'],4))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allwaves',required=True,help='Original FFCWS DS1 Stata or CSV dataset (local path)')
    parser.add_argument('--out',default='ffcws_attrition_results',help='Where aggregate files will be written')
    parser.add_argument('--male-code',type=int,default=1)
    parser.add_argument('--clip',type=float,default=0.02,help='Propensity floor, default .02')
    parser.add_argument('--odds',default='0.25,0.5,1,2,4',help='Assumed missing-outcome odds multipliers')
    parser.add_argument('--disclosure-n',type=int,default=15,help='Suppress demographic cells smaller than 15')
    parser.add_argument('--checksum',action='store_true',help='Compute source file SHA256 (slow on large file)')
    args=parser.parse_args()
    run(args)

if __name__=='__main__':main()
