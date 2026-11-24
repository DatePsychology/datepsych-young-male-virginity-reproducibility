#!/usr/bin/env python3
"""FFCWS narrow weighting/model robustness audit -- runs locally, aggregate-only outputs.

This script extends the earlier FFCWS attrition script. All row-level computations are
memory-only; neither identifiers nor individual-level predictions are written.
"""
from __future__ import annotations
import argparse
import json
import math
import hashlib
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import ConvergenceWarning
import ffcws_attrition_reference as ref

TEEN_VARS = {
    'k6d40': 'Year15 teen: ever smoked entire cigarette',
    'k6d48': 'Year15 teen: drank alcohol >2 times without parents',
    'k6f63': 'Year15 teen: ever tried marijuana',
    'k6d2b': 'Year15 teen: love life (psychosocial item)',
    'k6d61c': 'Year15 teen: ever took something from store',
}
FIXED = ['cm1bsex','k6f19','k6f26','k7e58','k7e59','k6natwt','k7natwt']
KNOWN = sorted(set(FIXED + ref.BASE_CATS + list(ref.BASE_CONT) + ref.R6 + ref.R7 + list(TEEN_VARS)))


def dataset_reader(path):
    path=Path(path)
    cols=set(KNOWN)
    if path.suffix.lower()=='.dta':
        with pd.io.stata.StataReader(str(path)) as reader:
            avail=list(reader.variable_labels().keys())
        selected=[v for v in avail if v.lower() in cols]
        d=pd.read_stata(path,columns=selected,convert_categoricals=False,convert_missing=False)
    elif path.suffix.lower()=='.csv':
        d=pd.read_csv(path,usecols=lambda c:c.lower() in cols,low_memory=False)
    else:
        raise ValueError('Input must be local .dta or .csv')
    d.columns=d.columns.str.lower()
    if d.columns.duplicated().any(): raise ValueError('Duplicate case-insensitive field names')
    absent=[c for c in FIXED + ref.R6 + ref.R7 if c not in d]
    if absent:raise ValueError('Missing required fields: '+', '.join(absent))
    return d


def teen_feature_block(d, min_n=20):
    """Codes are categorical; do not assume scale direction or interpret negative skip codes."""
    mats=[];names=[];availability=[]
    for v,label in TEEN_VARS.items():
        if v not in d:
            availability.append(dict(variable=v,label=label,available=False,usable_n=0,model_added=False))
            continue
        z=pd.to_numeric(d[v],errors='coerce')
        ok=z.ge(0)&z.notna()
        availability.append(dict(variable=v,label=label,available=True,
                                 usable_n=int(ok.sum()),model_added=bool(ok.sum()>=min_n and z[ok].nunique()>1)))
        if ok.sum()<min_n or z[ok].nunique()<2:continue
        ss=z.map(lambda x:'missing' if pd.isna(x) or x<0 else (str(int(x)) if float(x).is_integer() else str(x)))
        frequent=ss.value_counts()
        allowed=set(frequent[frequent>=15].index)
        ss=ss.map(lambda x:x if x in allowed else 'other')
        mat=pd.get_dummies(ss,prefix=v,drop_first=True).astype(float)
        if mat.shape[1]>15:raise ValueError(f'Unexpected code variety in {v}')
        if mat.shape[1]:
            mats.append(mat.to_numpy(float));names.extend(mat.columns.tolist())
    return (np.concatenate(mats,axis=1) if mats else np.empty((len(d),0)),names,availability)


def fit_sklearn(X,y,w,c,where=None):
    X=np.asarray(X,float); y=np.asarray(y,float);w=np.asarray(w,float)
    if where is None:where=np.ones(len(y),bool)
    mask=where&np.isfinite(y)&np.isfinite(w)&(w>0)
    if mask.sum()<20:raise ValueError('Under 20 positive-weight observations for model')
    yy=y[mask].astype(int)
    if np.unique(yy).size==1:return np.full(len(X),np.clip(yy[0],1e-4,1-1e-4))
    model=make_pipeline(StandardScaler(), LogisticRegression(C=c,solver='lbfgs',max_iter=2000,tol=1e-9))
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',ConvergenceWarning)
        model.fit(X[mask], yy, logisticregression__sample_weight=w[mask]/w[mask].mean())
    return model.predict_proba(X)[:,1]


def fit_scipy_independent(X,y,w,c,where=None):
    """Independent L2 logistic optimization, used to cross-check sklearn IPW results.

    sklearn minimizes sum(w_i * logloss_i) + ||beta||^2/(2*C) with an
    unpenalized intercept and normalized weights. Standardization here is
    independently implemented with NumPy, not sklearn's pipeline.
    """
    X=np.asarray(X,float);y=np.asarray(y,float);w=np.asarray(w,float)
    if where is None:where=np.ones(len(y),bool)
    mask=where&np.isfinite(y)&np.isfinite(w)&(w>0)
    yy=y[mask].astype(int);xx=X[mask];wt=w[mask]/np.mean(w[mask])
    if np.unique(yy).size==1:return np.full(len(X),np.clip(yy[0],1e-4,1-1e-4))
    center=xx.mean(axis=0); scale=xx.std(axis=0);scale[scale==0]=1.
    train=(xx-center)/scale; whole=(X-center)/scale
    nfeatures=train.shape[1];
    init=np.zeros(nfeatures+1)
    init[-1]=math.log(np.clip(np.dot(wt,yy)/wt.sum(),1e-5,1-1e-5)/np.clip(1-np.dot(wt,yy)/wt.sum(),1e-5,1-1e-5))
    def objective(beta):
        linear=train@beta[:-1]+beta[-1]
        pp=expit(linear)
        loss=np.dot(wt,np.logaddexp(0,linear)-yy*linear)+np.dot(beta[:-1],beta[:-1])/(2*c)
        err=wt*(pp-yy)
        grad=np.r_[train.T@err+beta[:-1]/c,err.sum()]
        return float(loss),grad
    opt=minimize(objective,init,jac=True,method='L-BFGS-B',options={'maxiter':5000,'ftol':1e-13,'gtol':1e-7})
    if not opt.success and np.linalg.norm(opt.jac,ord=np.inf)>1e-3:
        raise RuntimeError('Independent SciPy logistic fit failed: '+str(opt.message))
    return expit(whole@opt.x[:-1]+opt.x[-1])


def kish(w):
    w=np.asarray(w,float); w=w[np.isfinite(w)&(w>0)]
    return float(w.sum()**2/np.dot(w,w)) if len(w) else float('nan')


def weighted_mean(y,w):
    w=np.asarray(w,float);y=np.asarray(y,float)
    k=np.isfinite(y)&np.isfinite(w)&(w>0)
    return float(np.sum(w[k]*y[k])/np.sum(w[k])) if k.any() else float('nan')


def weight_summaries(ww):
    ww=np.asarray(ww,float); ww=ww[ww>0]
    if ww.size==0: return dict(ess=None,max_to_median=None,top1_weight_share=None,top5_weight_share=None)
    sorted_w=np.sort(ww)[::-1]
    return dict(ess=kish(ww),max_to_median=float(sorted_w[0]/np.median(ww)),
      top1_weight_share=float(sorted_w[:max(1,int(np.ceil(.01*len(ww))))].sum()/ww.sum()),
      top5_weight_share=float(sorted_w[:max(1,int(np.ceil(.05*len(ww))))].sum()/ww.sum()))


def weighted_cap(ww,pct):
    ww=np.asarray(ww,float).copy()
    # Only positive eligible sample weights, and the cap is recomputed in each jackknife replicate.
    q=float(np.quantile(ww[ww>0],pct))
    return np.minimum(ww,q)


def calc_model(y,w,x,c,clip,adjust='none',cut=.99, independent=False):
    valid=np.isfinite(y)&(w>0)
    if valid.sum()<20:raise ValueError('Not enough observed records')
    resp=np.isfinite(y).astype(float)
    fit = fit_scipy_independent if independent else fit_sklearn
    prop=fit(x,resp,w,c)
    prop=np.clip(prop,clip,1-clip)
    raw=w[valid]/prop[valid]
    if adjust=='total_cap':eff=weighted_cap(raw,cut)
    elif adjust=='response_cap':
        multiplier=1/prop[valid]
        cap=np.quantile(multiplier,cut)
        eff=w[valid]*np.minimum(multiplier,cap)
    elif adjust=='drop_top':
        cutoff=np.quantile(raw,cut)
        eff=np.where(raw>cutoff,0.,raw)
    elif adjust=='none':eff=raw
    else:raise ValueError('Unknown adjustment')
    result=weighted_mean(y[valid],eff)
    return result, prop, weight_summaries(eff)


def calc_aipw(y,w,x,c,clip):
    valid=np.isfinite(y)&(w>0)
    rr=np.isfinite(y).astype(float)
    pi=np.clip(fit_sklearn(x,rr,w,c),clip,1-clip)
    mu=np.clip(fit_sklearn(x,y,w,c,where=valid),1e-4,1-1e-4)
    correction=np.zeros(len(y),float)
    correction[valid]=(y[valid]-mu[valid])/pi[valid]
    return weighted_mean(mu+correction,w)


def jackknife_ratio(y,w,reps,mask):
    """Independent direct ratio and replicate SE, no original script helpers."""
    obs=np.asarray(mask,bool)&np.isfinite(y)
    def ratio(ww):
        ss=(np.asarray(ww,float)>0)&obs
        return float(np.sum(np.asarray(ww)[ss]*y[ss])/np.sum(np.asarray(ww)[ss]))
    est=ratio(w)
    r=np.array([ratio(rw) for rw in reps],float)
    return est,float(np.sqrt(np.sum((r-est)**2))),r


def main(args):
    out=Path(args.out).resolve();source=Path(args.allwaves).resolve()
    if out==source.parent:raise ValueError('Output folder must differ from microdata folder')
    out.mkdir(parents=True,exist_ok=True)
    df=dataset_reader(source)
    male,teen,adult=ref.classify(df,args.male_code)
    w6=ref.valid_weight(df['k6natwt']);w7=ref.valid_weight(df['k7natwt'])
    reps6=np.array([ref.valid_weight(df[x]) for x in ref.R6])
    reps7=np.array([ref.valid_weight(df[x]) for x in ref.R7])
    target=male&(teen==0)&(w6>0)
    years22=male&(teen==0)&np.isfinite(adult)&(w7>0)
    if target.sum()<200:raise ValueError('Unexpected Year 15 target count; check dataset and codes')
    yt=adult[target]; w=w6[target];x0,base_names,base_used=ref.covariate_matrix(df)
    teen_mat,teen_names,extra_presence=teen_feature_block(df)
    xf=x0[target]
    x_simple_full,x_names_simple,_=ref.covariate_matrix(df.drop(columns=[c for c in ['cm1povca','cm1relf'] if c in df.columns]))
    X={
       'baseline':xf,
       'parsimonious':x_simple_full[target],
       'teen_enriched':np.column_stack([xf,teen_mat[target]]) if teen_mat.shape[1] else xf,
    }
    features={'baseline':base_names,'parsimonious':x_names_simple,'teen_enriched':base_names+teen_names}
    # Reproduce original two independently calculated survey-weighted ratios.
    check=[]
    cc,cc_se,cc_rep=jackknife_ratio(yt,w,reps6[:,target],np.isfinite(yt))
    yy=adult[years22];ww=w7[years22]
    y22,y22_se,y22_rep=jackknife_ratio(yy,ww,reps7[:,years22],np.isfinite(yy))
    for name, est,se in [('year15_complete_case',cc,cc_se),('year22_original_complete_case',y22,y22_se)]:
        check.append(dict(check=name,estimate=est,se=se,n_observed=int(np.isfinite(yt).sum() if name.startswith('year15') else len(yy)),matches_previous=bool(abs(est-(.80328317 if name.startswith('year15') else .80071903))<.003)))
    if args.strict and not all(q['matches_previous'] for q in check):
        raise RuntimeError('A historical estimate did not reproduce within 0.3 percentage points; inspect dataset version.')
    specs=[
       ('baseline_ipw','baseline',1.,.02,'none',.99),
       ('baseline_aipw','baseline',1.,.02,'aipw',.99),
       ('parsimonious_ipw','parsimonious',1.,.02,'none',.99),
       ('enriched_ipw','teen_enriched',1.,.02,'none',.99),
       ('enriched_aipw','teen_enriched',1.,.02,'aipw',.99),
       ('enriched_weak_ridge','teen_enriched',10.,.02,'none',.99),
       ('enriched_strong_ridge','teen_enriched',.1,.02,'none',.99),
       ('baseline_clip_05','baseline',1.,.05,'none',.99),
       ('baseline_clip_10','baseline',1.,.10,'none',.99),
       ('baseline_ipw_total_cap_99','baseline',1.,.02,'total_cap',.99),
       ('baseline_ipw_total_cap_95','baseline',1.,.02,'total_cap',.95),
       ('baseline_ipw_response_cap_95','baseline',1.,.02,'response_cap',.95),
       ('baseline_drop_highest_1pct','baseline',1.,.02,'drop_top',.99),
    ]
    observed=int(np.isfinite(yt).sum())
    rows=[]; print('Computing prespecified model variants and 33-replicate refits...',flush=True)
    for j,(label,x_name,C,cl,adj,pct) in enumerate(specs,1):
        xx=X[x_name]
        if adj=='aipw':
            est=calc_aipw(yt,w,xx,C,cl); di=weight_summaries(w[np.isfinite(yt)])
            rf=[calc_aipw(yt,rw,xx,C,cl) for rw in reps6[:,target]]
        else:
            est,p,di=calc_model(yt,w,xx,C,cl,adj,pct)
            rf=[calc_model(yt,rw,xx,C,cl,adj,pct)[0] for rw in reps6[:,target]]
        se=float(np.sqrt(np.sum((np.array(rf)-est)**2)))
        rows.append(dict(specification=label,model=x_name,c=C,propensity_floor=cl,
                         weight_treatment=adj,cap_quantile=pct,n_domain=int(target.sum()),n_observed=observed,
                         estimate=est,se_jackknife=se,ci_low=max(0.,est-1.96*se),ci_high=min(1.,est+1.96*se),
                         weight_ess=di['ess'],max_weight_to_median=di['max_to_median'],
                         top1_weight_share=di['top1_weight_share'],top5_weight_share=di['top5_weight_share']))
        print(f' {j:02d}/{len(specs)} {label}: {est:.4f} (SE {se:.4f})',flush=True)
    pd.DataFrame(rows).to_csv(out/'model_variants.csv',index=False,float_format='%.9g')
    pd.DataFrame(check).to_csv(out/'jackknife_ratio_crosscheck.csv',index=False,float_format='%.9g')
    # Independent logistic optimizer, including full independent replicate refits.
    base_model=next(a for a in rows if a['specification']=='baseline_ipw')
    ind,_,di=calc_model(yt,w,X['baseline'],1.,.02,independent=True)
    indreps=np.array([calc_model(yt,rw,X['baseline'],1.,.02,independent=True)[0] for rw in reps6[:,target]])
    indse=float(np.sqrt(np.sum((indreps-ind)**2)))
    if abs(ind-base_model['estimate'])>.003 or abs(indse-base_model['se_jackknife'])>.003:
        warnings.warn('Independent SciPy IPW differs >0.3pp from sklearn in point or SE. Inspect solver diagnostics.')
    pd.DataFrame([dict(estimator='Python sklearn baseline IPW',point=base_model['estimate'],se=base_model['se_jackknife'],
                       independent_method=False),
                  dict(estimator='Independent SciPy L-BFGS-B baseline IPW',point=ind,se=indse,independent_method=True),
                  dict(estimator='Direct NumPy Year15 complete-case ratio',point=cc,se=cc_se,independent_method=True),
                  dict(estimator='Direct NumPy Year22 complete-case ratio',point=y22,se=y22_se,independent_method=True)])\
      .to_csv(out/'independent_solver_check.csv',index=False,float_format='%.9g')
    pd.DataFrame(extra_presence).to_csv(out/'teen_predictor_availability.csv',index=False)
    # Stable, aggregate-only response model calibration by coarse quintiles, all eligible.
    prop=np.clip(fit_sklearn(X['baseline'],np.isfinite(yt).astype(float),w,1.),.02,.98)
    ranks=pd.Series(prop).rank(method='first',pct=True).to_numpy()
    cal=[]
    for i in range(5):
        binmask=(ranks>=i/5)&(ranks<=(i+1)/5) if i==0 else ((ranks>i/5)&(ranks<=(i+1)/5))
        if binmask.sum()<args.min_cell:continue
        cal.append(dict(quantile_group=i+1,n=int(binmask.sum()),predicted_response=weighted_mean(prop[binmask],w[binmask]),
                        observed_response=weighted_mean(np.isfinite(yt)[binmask].astype(float),w[binmask])))
    pd.DataFrame(cal).to_csv(out/'response_calibration.csv',index=False)
    # Independent algebraic sharp bounds. They are unaffected by any model or trimming.
    overall_weight=w.sum(); obs=np.isfinite(yt)
    weighted_known_positive=np.sum(w[obs]*yt[obs])/overall_weight
    missing_weight=w[~obs].sum()/overall_weight
    bounds=[dict(assumption='all_missing_no',rate=weighted_known_positive),
            dict(assumption='all_missing_yes',rate=weighted_known_positive+missing_weight)]
    pd.DataFrame(bounds).to_csv(out/'original_frame_bounds.csv',index=False,float_format='%.9g')
    meta=dict(project='FFCWS narrow weighting/model robustness audit',date_run='local',
         does_not_export_microdata=True,n_rows=int(len(df)),n_target=int(target.sum()),n_followup=int(obs.sum()),
         sex_code=args.male_code,baseline_features=base_names,teen_features=teen_names,
         teen_vars=extra_presence,robustness_specs=[r[0] for r in specs],
         independent_scipy_point_difference=float(ind-base_model['estimate']),
         independent_scipy_se_difference=float(indse-base_model['se_jackknife']),
         year15_weighted_bounds=[float(x['rate']) for x in bounds],
         warning='Not a direct population longitudinal weight; replicate-based variance is design-informed; no inference for missing Year15 status or later cohorts.',
         icpsr_input_sha256='Not calculated (avoid slow hashing); use local path only.')
    (out/'audit_metadata.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    print('Done. Please share only the six aggregate CSVs and audit_metadata.json in',out,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allwaves',required=True)
    parser.add_argument('--out',default='FFCWS-Weight-Model-Robustness-Results')
    parser.add_argument('--male-code',type=int,default=1)
    parser.add_argument('--strict',action='store_true',help='Stop if 2026 baseline estimates differ from previous by >0.3pp')
    parser.add_argument('--min-cell',type=int,default=15,help='Small calibration groups suppressed')
    main(parser.parse_args())
