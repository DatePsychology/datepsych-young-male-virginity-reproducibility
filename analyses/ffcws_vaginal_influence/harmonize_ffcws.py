#!/usr/bin/env python3
"""FFCWS Year-15 to Year-22 male sexual experience harmonization.

Use only on an authorized local copy of ICPSR 31622 DS0001. Never exports rows,
IDs, individual predictions, or any respondent-level data. Aggregate only.

Survey-contrast outcome is vaginal intercourse in the FFCWS YA questionnaire;
not exactly the NSFG's penile-vaginal intercourse with a woman.
"""
from __future__ import annotations
import argparse, json, math, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import ffcws_attrition_reference as prior

NREP=33
REPS6=[f'k6natwt_rep{i}' for i in range(1, NREP+1)]
REPS7=[f'k7natwt_rep{i}' for i in range(1, NREP+1)]
REQUIRED=['cm1bsex','k6f19','k6f26','k7e58','k7e59','k7e60',
          'ck6yagem','ck7yagem','k6natwt','k7natwt']+REPS6+REPS7
SELECT=set(REQUIRED+prior.BASE_CATS+list(prior.BASE_CONT))


def numeric(df, name):
    return pd.to_numeric(df[name], errors='coerce').to_numpy(float)


def read_restricted(path):
    path=Path(path)
    if path.suffix.lower()=='.dta':
        with pd.io.stata.StataReader(str(path)) as reader:
            names=list(reader.variable_labels())
        chosen=[name for name in names if name.lower() in SELECT]
        df=pd.read_stata(path, columns=chosen, convert_categoricals=False, convert_missing=False)
    elif path.suffix.lower()=='.csv':
        df=pd.read_csv(path, usecols=lambda col:col.lower() in SELECT, low_memory=False)
    else:
        raise ValueError('Supply .dta or .csv')
    df.columns=df.columns.str.lower()
    if df.columns.duplicated().any():raise ValueError('Duplicate case-insensitive columns')
    missing=[c for c in REQUIRED if c not in df]
    if missing:raise ValueError('Required variables unavailable: '+', '.join(missing))
    return df


def code_outcomes(d):
    """No inference from negative codes except known questionnaire-required skips.

    k7e58 no logically entails no vaginal intercourse (E59 intentionally skipped).
    Contradictory yes-vaginal/no-any rows are left unknown for both outcomes.
    """
    male=(numeric(d,'cm1bsex')==1)
    y15_partner=numeric(d,'k6f19'); y15_general=numeric(d,'k6f26')
    teen=np.full(len(d),np.nan)
    teen[(y15_partner==1)|(y15_general==1)]=1
    teen[(y15_general==2)&(y15_partner!=1)]=0
    raw_any=numeric(d,'k7e58');raw_v=numeric(d,'k7e59'); raw_debut=numeric(d,'k7e60')
    mismatch=(raw_any==2)&(raw_v==1)
    anysex=np.full(len(d),np.nan);vaginal=np.full(len(d),np.nan)
    anysex[raw_any==1]=1;anysex[raw_any==2]=0
    vaginal[raw_v==1]=1; vaginal[raw_v==2]=0
    vaginal[(raw_any==2)&(raw_v!=1)]=0
    anysex[mismatch]=np.nan;vaginal[mismatch]=np.nan
    debut=np.where((raw_debut>=5)&(raw_debut<=30),raw_debut,np.nan)
    # Never treat refusal/don't-know/out-of-range as zero age.
    age15m=numeric(d,'ck6yagem'); age22m=numeric(d,'ck7yagem')
    age15m=np.where((age15m>=144)&(age15m<240),age15m,np.nan)
    age22m=np.where((age22m>=216)&(age22m<360),age22m,np.nan)
    return dict(male=male, teen=teen, anysex=anysex, vaginal=vaginal,
                age_first=debut, age15m=age15m,age22m=age22m,
                raw_any=raw_any, raw_vag=raw_v,raw_debut=raw_debut, mismatch=mismatch)


def survey_stats(y, domain, w, reps):
    y=np.asarray(y,float); dom=np.asarray(domain,bool); w=np.asarray(w,float)
    ok=dom & np.isfinite(y)&np.isfinite(w)&(w>0)
    if not ok.any():
        return dict(n_eligible=int(dom.sum()),n_observed=0,estimate=None,se=None,ci_low=None,ci_high=None,
                    observed_weight_fraction=None,replicates_valid=0)
    # Conservative disclosure safety for sensitive outcomes. Withhold cell estimates
    # based on fewer than 10 observed cases or a nonzero 1--9 success/failure cell.
    nobs=int(ok.sum()); n1=int(np.sum(ok&(y==1))); n0=int(np.sum(ok&(y==0)))
    if (0<nobs<10) or (0<n1<10) or (0<n0<10) or (0<int(np.sum(dom))<10):
        return dict(n_eligible=count_safe(int(dom.sum())),
                    n_observed=count_safe(nobs),estimate=None,se=None,
                    ci_low=None,ci_high=None,observed_weight_fraction=None,replicates_valid=0)
    def weighted(ww):
        valid=dom&np.isfinite(y)&np.isfinite(ww)&(ww>0)
        return float(np.dot(y[valid],ww[valid])/ww[valid].sum()) if valid.any() else np.nan
    p=weighted(w)
    rr=np.array([weighted(wrep) for wrep in reps],float)
    if not np.all(np.isfinite(rr)):raise ValueError('Invalid jackknife ratio replicate')
    se=float(np.sqrt(np.sum((rr-p)**2)))
    eligible_w=w[dom&(w>0)].sum()
    return dict(n_eligible=int(np.sum(dom&(w>0))),n_observed=int(ok.sum()),estimate=p,se=se,
                ci_low=max(0.,p-1.96*se),ci_high=min(1.,p+1.96*se),
                observed_weight_fraction=float(w[ok].sum()/eligible_w) if eligible_w>0 else None,
                replicates_valid=NREP)


def ipw_stats(y, domain, w, reps, X, *, c=1.,clip=0.02):
    """Re-estimate response model in each replicate on common baseline covariates."""
    y=np.asarray(y,float); domain=np.asarray(domain,bool)
    xx=np.asarray(X,float)
    idx=np.flatnonzero(domain&(w>0))
    if len(idx)<30:return dict(estimate=None,se=None,ci_low=None,ci_high=None, n_observed=0)
    yy=y[idx];xx=xx[idx];wt=np.asarray(w,float)[idx];rwt=np.asarray(reps,float)[:,idx]
    response=np.isfinite(yy)
    if response.sum()<20 or (~response).sum()==0:
        return dict(estimate=None,se=None,ci_low=None,ci_high=None,n_observed=int(response.sum()))
    def one(ww):
        pi=prior.fit_prob(xx,response.astype(float),ww,clamp=(clip,1-clip))
        return prior.wmean(yy[response],ww[response]/pi[response])
    p=one(wt);rep=np.array([one(ww) for ww in rwt]);
    if not np.isfinite(rep).all(): raise ValueError('Nonfinite response model replica')
    se=float(np.sqrt(np.sum((rep-p)**2)))
    return dict(estimate=p,se=se,ci_low=max(0,p-1.96*se),ci_high=min(1,p+1.96*se),
                n_observed=int(response.sum()))


def new_record(section, label, domain_name, mode, outcome, domain, w, reps, X=None):
    r=survey_stats(outcome,domain,w,reps)
    if mode=='ipw':
        adjusted=ipw_stats(outcome,domain,w,reps,X)
        r.update(adjusted)
    return {'section':section,'measure':label,'domain':domain_name,'estimator':mode,**r}


def count_safe(n):
    if 0<n<10:return '<10'
    return int(n)


def run(args):
    input_path=Path(args.allwaves).resolve(); out=Path(args.out).resolve()
    if input_path.parent==out:raise ValueError('--out must not be the microdata directory')
    out.mkdir(parents=True, exist_ok=True)
    d=read_restricted(input_path)
    if len(d)<1000:raise ValueError('Expected all-wave study; too few rows')
    st=code_outcomes(d)
    male=st['male']; teen=st['teen'];anysex=st['anysex'];vag=st['vaginal'];a=st['age_first'];m6=st['age15m'];m7=st['age22m']
    w6=prior.valid_weight(d['k6natwt']);w7=prior.valid_weight(d['k7natwt'])
    reps6=np.array([prior.valid_weight(d[k]) for k in REPS6]);reps7=np.array([prior.valid_weight(d[k]) for k in REPS7])
    base_X,feature_names,_=prior.covariate_matrix(d)
    target=male & (teen==0) & (w6>0)
    original=male&(teen==0)&(w7>0)
    if args.strict and (int(target.sum())!=938 or int(np.sum(original & np.isfinite(anysex)))!=701):
        raise ValueError(f'Strict sample check failed: age15 national={target.sum()}, historical Year22 complete={np.sum(original & np.isfinite(anysex))}. Check release and classification.')
    # Primary measurement comparison on matched denominator (any sex and vaginal both valid).
    matched=np.isfinite(anysex)&np.isfinite(vag)
    gap=np.where(matched,anysex-vag,np.nan)
    # Paired single-source gaps, not comparisons of incompatible denominators.
    core=[]
    for label,y in [('any_sex',anysex),('vaginal_intercourse',vag),('any_sex_matched',np.where(matched,anysex,np.nan)),
                     ('vaginal_matched',np.where(matched,vag,np.nan)),('sex_without_vaginal_matched',gap)]:
        for design,dom,ww,rr in [('year15',target,w6,reps6),('year22',original,w7,reps7)]:
            core.append(new_record('outcomes',label,design,'complete_case',y,dom,ww,rr))
            if design=='year15':
                core.append(new_record('outcomes',label,design,'ipw',y,dom,ww,rr,base_X))
    pd.DataFrame(core).to_csv(out/'harmonized_outcomes.csv',index=False, float_format='%.10g')
    # Unconditional partial-identification bounds on the original Year-15-weighted
    # target: missing adult status could be either zero or one.
    missing_bounds=[]
    for label,y in [('any_sex',anysex),('vaginal_intercourse',vag)]:
        for assumption,z in [('all_missing_no',np.where(np.isfinite(y),y,0.)),
                             ('all_missing_yes',np.where(np.isfinite(y),y,1.))]:
            missing_bounds.append({'measure':label,'assumption':assumption,
                                   **survey_stats(z,target,w6,reps6)})
    pd.DataFrame(missing_bounds).to_csv(out/'outcome_missingness_bounds.csv',index=False,float_format='%.10g')
    paired=[r for r in core if r['measure'] in ['any_sex_matched','vaginal_matched','sex_without_vaginal_matched']]
    pd.DataFrame(paired).to_csv(out/'matched_outcome_gap.csv',index=False,float_format='%.10g')
    # Direct comparison with prior aggregate estimates (these are historical, not new microdata).
    org_any=survey_stats(anysex, original,w7,reps7)
    org_vag=survey_stats(vag,original,w7,reps7)
    if args.strict:
        if abs(org_any['estimate']-0.800719)>0.002 or abs(org_vag['estimate']-0.7426492)>0.002:
            raise ValueError('Historical estimates mismatch; check survey release or coding.')
    # Year 22 attained-age distribution -- age is subject's, not subject's child.
    age_rows=[]
    bands=[('under_21',0,252),('21_to_before_22',252,264),('22_to_before_23',264,276),
           ('23_to_before_24',276,288),('24_or_more',288,360)]
    for label,lo,hi in bands:
        m=target & (m7>=lo) & (m7<hi)
        n=int(m.sum())
        age_rows.append(dict(group='young_adult_interview_age',age_band=label,n=count_safe(n),
                  proportion_of_known_age_y15_frame=prior.wmean(m[ target & np.isfinite(m7)],w6[target & np.isfinite(m7)]) if n>=10 else None))
    t_bands=[('under_15',0,180),('15_to_before_16',180,192),('16_to_before_17',192,204),
             ('17_or_more',204,240)]
    for label,lo,hi in t_bands:
        m=target & (m6>=lo) & (m6<hi)
        n=int(m.sum())
        age_rows.append(dict(group='adolescent_interview_age',age_band=label,n=count_safe(n),
                 proportion_of_known_age_y15_frame=prior.wmean(m[target & np.isfinite(m6)],w6[target & np.isfinite(m6)]) if n>=10 else None))
    pd.DataFrame(age_rows).to_csv(out/'interview_age_profile.csv',index=False,float_format='%.10g')
    # Age-at-first categories conditional on reported vaginal intercourse and valid debut age.
    debut_rows=[]
    for label,lo,hi in [('before_16',0,16),('16_to_17',16,18),('18_to_19',18,20),
                        ('20_to_21',20,22),('22_or_later',22,40)]:
        y=np.where(np.isfinite(a),((a>=lo)&(a<hi)).astype(float),np.nan)
        for design,dom,w,rr in [('year15',target & (vag==1),w6,reps6),('year22',original & (vag==1),w7,reps7)]:
            stat=survey_stats(y,dom,w,rr)
            debut_rows.append({'age_first_band':label,'domain':design,**stat})
    pd.DataFrame(debut_rows).to_csv(out/'age_at_first_vaginal.csv',index=False,float_format='%.10g')
    # Fixed milestone at a birthday: ONLY respondents already at/past that age when interviewed.
    # If vaginal=yes but debut age missing, event before birthday remains unknown.
    birthday=[]
    for cutoff in [18,20,21,22,23]:
        age_domain=target & np.isfinite(m7)&(m7>=cutoff*12)
        y=np.full(len(d),np.nan)
        y[(vag==0)&age_domain]=0
        confirmed=(vag==1)&np.isfinite(a)&age_domain
        y[confirmed]=(a[confirmed]<cutoff).astype(float)
        lower=np.where(np.isfinite(y),y,0.)
        upper=np.where(np.isfinite(y),y,1.)
        for label,measure in [('complete_cases',y),('missing_debut_all_no',lower),('missing_debut_all_yes',upper)]:
            r=survey_stats(measure,age_domain,w6,reps6)
            birthday.append({'cutoff_birthday':cutoff,'scenario':label,**r})
    pd.DataFrame(birthday).to_csv(out/'birthday_milestones.csv',index=False,float_format='%.10g')
    # Age-15 interview initially no intercourse: by vaginal-first age this may be uncertain
    # if age-first and age-at-Y15 are the same integer age.
    age15_completed=np.where(np.isfinite(m6),np.floor(m6/12),np.nan)
    chronology_certain=target&(vag==1)&np.isfinite(a)&np.isfinite(age15_completed)&(a<age15_completed)
    chronology_same=target&(vag==1)&np.isfinite(a)&np.isfinite(age15_completed)&(a==age15_completed)
    first_after=target&(vag==1)&np.isfinite(a)&np.isfinite(age15_completed)&(a>age15_completed)
    future_debut=target&(vag==1)&np.isfinite(a)&np.isfinite(m7)&(a>np.floor(m7/12))
    if np.any(future_debut):
        warnings.warn('Some retrospectively reported first-vaginal ages are after age at interview; see audit')
    audits=[]
    masks={'male_at_baseline':male,
           'male_valid_year15_status':male&np.isfinite(teen),
           'male_year15_no_intercourse':male&(teen==0),
           'male_year15_no_and_national_weight':target,
           'year15_no_year22_any_known':target&np.isfinite(anysex),
           'year15_no_year22_vaginal_known':target&np.isfinite(vag),
           'year15_no_both_adult_outcomes_known':target&matched,
           'year15_no_vaginal_yes_debut_age_known':target&(vag==1)&np.isfinite(a),
           'year15_no_vaginal_yes_debut_age_missing':target&(vag==1)&~np.isfinite(a),
           'year15_no_young_adult_age_missing':target&~np.isfinite(m7),
           'year15_no_adolescent_age_missing':target&~np.isfinite(m6),
           'year15_no_debut_definitely_before_teen_interview_age':chronology_certain,
           'year15_no_debut_same_integer_age_as_teen_interview':chronology_same,
           'year15_no_debut_clearly_after_teen_interview_age':first_after,
           'year15_no_debut_reported_after_year22_interview_age':future_debut,
           'adult_no_any_but_yes_vaginal_inconsistent':male&st['mismatch'],
           'age15_yes_adult_no_any_inconsistent':male&(teen==1)&(anysex==0),
           'year15_no_adult_any_yes_vaginal_no':target&(anysex==1)&(vag==0),
           'year15_no_year22_vaginal_directly_no':target&(st['raw_vag']==2),
           'year15_no_year22_vaginal_no_inferred_by_skip':target&(st['raw_any']==2)&(st['raw_vag']!=1)}
    for lab,mask in masks.items():
        n=int(np.sum(mask)); audits.append({'check':lab,'n':count_safe(n),
                  'national_year15_weight_share':prior.wmean(mask[target],w6[target]) if n>=10 else None})
    pd.DataFrame(audits).to_csv(out/'routing_and_quality_audit.csv',index=False,float_format='%.10g')
    # Alternative adolescents exactly 15 at interview. Do not silently equate wave with age.
    age15at15=target & np.isfinite(m6) & (m6>=180)&(m6<192)
    age_sub=[]
    for measure,y in [('any_sex_y22',anysex),('vaginal_y22',vag)]:
        age_sub.append({'measure':measure,'domain':'interview_age_15_to_before_16',
                        **survey_stats(y,age15at15,w6,reps6)})
    pd.DataFrame(age_sub).to_csv(out/'age15_restricted_outcomes.csv',index=False,float_format='%.10g')
    metadata={
       'description':'FFCWS local-only Year15 to Year22 vaginal-intercourse harmonization',
       'allwaves_file_name_only':input_path.name,'records_imported':int(len(d)),
       'n_target_year15_no_national':int(target.sum()),
       'n_original_year22_any_valid':int(np.sum(original&np.isfinite(anysex))),
       'n_matched_year15_domain':int(np.sum(target&matched)),
       'n_year22_age_observed_year15_domain':int(np.sum(target&np.isfinite(m7))),
       'date_executed':'local',
       'definitions':{
        'age15':'k6f19=1 or k6f26=1 means ever intercourse; k6f26=2 and k6f19!=1 means no; else missing',
        'year22_any':'k7e58 1=yes 2=no',
        'year22_vaginal':'k7e59 1=yes 2=no; if k7e58=2 and e59 skipped, vaginal=no; inconsistent rows unknown',
        'age_first':'k7e60 completed integer age at first vaginal sexual intercourse, among vaginal yes',
        'interview_ages':'ck6yagem and ck7yagem are RESPONDENT ages in months; ck7childageinterviewm is G3 child age and MUST NOT be used',
        'birthday':'only respondents interviewed at or after birthday; yes if first-vaginal age strictly < birthday, no if no vaginal by interview',
        'percentages':'fractions on [0,1], multiply by 100 to display as percentages',
        'weighting':'wave-specific k6natwt (main) and k7natwt (historical sensitivity), 33 replicate weights, multiplier 1 mse',
        'limitations':'Year 15 question does not explicitly specify vaginal intercourse; Year 22 vaginal sex does not specify sex of partner; cohort born 1998-2000 in large cities; age-at-first retrospective/rounded; selective attrition; no longitudinal weights.'
       },
       'files':['harmonized_outcomes.csv','matched_outcome_gap.csv','interview_age_profile.csv',
                'age_at_first_vaginal.csv','birthday_milestones.csv','outcome_missingness_bounds.csv',
                'routing_and_quality_audit.csv','age15_restricted_outcomes.csv','analysis_metadata.json'],
    }
    (out/'analysis_metadata.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    # Report limited to aggregate numbers; never write observations or predictions.
    def fmt(method,design='year15',model='complete_case'):
        r=next(x for x in core if x['measure']==method and x['domain']==design and x['estimator']==model)
        return f"{100*r['estimate']:.2f}% (n={r['n_observed']}, 95% CI {100*r['ci_low']:.2f}–{100*r['ci_high']:.2f}%)"
    text='# Locally executed FFCWS harmonization: aggregate summary\n\n'
    text+=f'- Age-15 initially reporting no intercourse (Year-15 national sample): **{target.sum()}**.\n'
    text+=f'- Year-22 any sex: **{fmt("any_sex")}**.\n'
    text+=f'- Year-22 vaginal intercourse: **{fmt("vaginal_intercourse")}**.\n'
    text+=f'- Paired any sex, identical denominator: **{fmt("any_sex_matched")}**.\n'
    text+=f'- Paired vaginal intercourse, identical denominator: **{fmt("vaginal_matched")}**.\n'
    text+=f'- Paired any sex minus vaginal intercourse: **{fmt("sex_without_vaginal_matched")}**.\n'
    b=next(z for z in missing_bounds if z['measure']=='vaginal_intercourse' and z['assumption']=='all_missing_no')
    text+=f'- Vaginal intercourse under all missing outcomes assumed NO: **{100*b["estimate"]:.2f}%** (point bound, not a confidence limit).\n'
    text+='\nInterpretation: vaginal intercourse is closer to NSFG, but FFCWS Year-15 intercourse and gender of vaginal partner are not identically defined. Fixed-birthday estimates only cover respondents old enough at interview. See CSV for exact results and checks.\n'
    (out/'SUMMARY.md').write_text(text,encoding='utf-8')
    print(text)
    print('Saved aggregate-only results to',out)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--allwaves',required=True,help='Authorized local ICPSR DS0001 Stata .dta or CSV')
    p.add_argument('--out',default='FFCWS-Harmonized-Results',help='Separate aggregate output directory')
    p.add_argument('--strict',action='store_true',help='Require previous local analysis sample and estimates to match')
    run(p.parse_args())
