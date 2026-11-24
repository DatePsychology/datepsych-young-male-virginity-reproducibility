#!/usr/bin/env python3
"""FFCWS Y15->Y22 chronology forensics. Run locally under authorized ICPSR access.

Only privacy-screened aggregate CSV/JSON outputs; no person-level records or IDs.
The resulting estimates describe REPORTED histories, not verified life events.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd

NREP=33
REPS=[f'k6natwt_rep{i}' for i in range(1,NREP+1)]
NEED=['cm1bsex','k6f19','k6f26','k7e58','k7e59','k7e60',
      'ck6yagem','ck7yagem','k6natwt']+REPS
OPTIONAL=['k6f20','k6f20a','k6f21','k6f29','k6f30','k6f30a','k6f31',
          'k7e62','k7e64']

def load(path:Path)->pd.DataFrame:
    sought=set(NEED+OPTIONAL)
    if path.suffix.lower()=='.dta':
        with pd.io.stata.StataReader(str(path)) as rdr:
            available=list(rdr.variable_labels())
        selected=[c for c in available if c.lower() in sought]
        d=pd.read_stata(path,columns=selected,convert_categoricals=False,
                        convert_missing=False)
    elif path.suffix.lower()=='.csv':
        d=pd.read_csv(path,usecols=lambda s:s.lower() in sought,low_memory=False)
    else: raise ValueError('Expected a Stata .dta or CSV dataset')
    d.columns=d.columns.str.lower()
    if d.columns.duplicated().any():raise ValueError('Duplicate case-insensitive columns')
    absent=[x for x in NEED if x not in d]
    if absent:raise ValueError('Missing required variables: '+', '.join(absent))
    return d

def num(d:pd.DataFrame,k:str)->np.ndarray:
    if k not in d:return np.full(len(d),np.nan)
    return pd.to_numeric(d[k],errors='coerce').to_numpy(dtype=float)

def wmean(y,w):
    valid=np.isfinite(y)&np.isfinite(w)&(w>0)
    if not np.any(valid):return np.nan
    return float(np.dot(y[valid],w[valid])/w[valid].sum())

def safe_n(n:int):
    return '<10' if 0<n<10 else int(n)

def design_rate(domain, event, w, reps):
    """Event as a binary on domain. Replicate MSE-centred multiplier=1.

    Privacy: hide positive/negative counts of 1--9 and any denominator <10.
    """
    domain=np.asarray(domain,bool);event=np.asarray(event,bool)
    n=int(domain.sum());k=int((domain&event).sum());other=n-k
    base={'n_domain':safe_n(n),'n_event':safe_n(k)}
    if n<10 or 0<k<10 or 0<other<10:
        return dict(**base,share=None,se=None,ci_low=None,ci_high=None)
    if not n: return dict(**base,share=None,se=None,ci_low=None,ci_high=None)
    sub=event[domain].astype(float);wg=w[domain];rr=reps[:,domain]
    p=wmean(sub,wg)
    replicates=np.asarray([wmean(sub,v) for v in rr])
    if not np.all(np.isfinite(replicates)):
        raise ValueError('Replicate includes a missing/zero-weight domain')
    se=float(np.sqrt(np.sum(np.square(replicates-p))))
    return dict(**base,share=p,se=se,ci_low=max(0,p-1.96*se),
                ci_high=min(1,p+1.96*se))

def label_array(masks, n):
    out=np.full(n,'unclassified',dtype=object)
    for label,mask in masks:out[mask]=label
    return out

def run(datafile:Path, out:Path,strict:bool=False):
    datafile=datafile.resolve();out=out.resolve()
    if out==datafile.parent:
        raise ValueError('Do not write results to your restricted-data directory')
    out.mkdir(parents=True,exist_ok=True)
    d=load(datafile);n=len(d)
    v={k:num(d,k) for k in NEED+OPTIONAL}
    w=np.where(np.isfinite(v['k6natwt'])&(v['k6natwt']>0),v['k6natwt'],0.)
    reps=np.stack([np.where(np.isfinite(v[k])&(v[k]>0),v[k],0.) for k in REPS])
    f19=v['k6f19'];f26=v['k6f26'];e58=v['k7e58'];e59=v['k7e59'];debut=v['k7e60']
    months15=v['ck6yagem']; months22=v['ck7yagem']
    months15=np.where((months15>=144)&(months15<240),months15,np.nan)
    months22=np.where((months22>=216)&(months22<360),months22,np.nan)
    first=np.where((debut>=5)&(debut<=30),debut,np.nan)
    male=v['cm1bsex']==1
    teen=np.full(n,np.nan)
    teen[(f19==1)|(f26==1)]=1.
    teen[(f26==2)&(f19!=1)]=0.
    vaginal=np.full(n,np.nan)
    vaginal[e59==1]=1;vaginal[e59==2]=0
    vaginal[(e58==2)&(e59!=1)]=0
    contradiction_e58=(e58==2)&(e59==1)
    vaginal[contradiction_e58]=np.nan
    target=male&(teen==0)&(w>0)
    both=target&(vaginal==1)&np.isfinite(first)&np.isfinite(months15)
    teen_completed=np.floor(months15/12)
    pre=both&(first<teen_completed)
    same=both&(first==teen_completed)
    post=both&(first>teen_completed)
    adult_yes_undated=target&(vaginal==1)&~np.isfinite(first)
    adult_unknown=target&~np.isfinite(vaginal)
    adult_known_no=target&(vaginal==0)
    year15_teen_yes=male&(teen==1)&(w>0)
    y22_any_no=(e58==2)
    if strict and (target.sum()!=938 or (target & np.isfinite(vaginal)).sum()!=697 or
                   pre.sum()!=49 or same.sum()!=52 or post.sum()!=402):
        raise ValueError('Expected original case counts not reproduced. Investigate release, variable coding, or frame; do not silently proceed.')
    main={
        'reported_age_earlier_than_y15':pre,
        'reported_same_completed_age':same,
        'reported_age_strictly_after_y15':post,
        'adult_vaginal_yes_age_missing':adult_yes_undated,
        'adult_vaginal_outcome_missing':adult_unknown,
        'adult_known_no_vaginal':adult_known_no,
        'adult_known_yes_vaginal':target&(vaginal==1),
        'adult_known_any_vaginal_status':target&np.isfinite(vaginal),
    }
    rows=[]
    for name,mask in main.items():
        rows.append({'category':name,**design_rate(target,mask,w,reps)})
    pd.DataFrame(rows).to_csv(out/'chronology_components.csv',index=False,float_format='%.12g')
    # Classification envelope conditional on assuming the rounded adult debut age is accurate.
    # This is NOT a bound on the truth if retrospective first-age reports are inaccurate.
    envelope={
        'confirmed_after_only':post,
        'confirmed_after_plus_same_age_possible':post|same,
        'confirmed_after_plus_same_age_and_undated_yes':post|same|adult_yes_undated,
        'possible_after_including_missing_adult_outcomes':post|same|adult_yes_undated|adult_unknown,
        'reported_adult_vaginal_yes_known_or_missing_as_no':target&(vaginal==1),
    }
    erows=[]
    for label,mask in envelope.items():
        erows.append({'scenario':label,'meaning':'Classification sensitivity, not a correction for reporting errors',
                      **design_rate(target,mask,w,reps)})
    pd.DataFrame(erows).to_csv(out/'classification_envelope.csv',index=False,float_format='%.12g')
    # Reporting route. No relies on explicit lifetime NO at F26; F19 only distinguishes pathway.
    route=label_array([
        ('no_current_partner_or_f19_skipped',target&~np.isin(f19,[1.,2.])),
        ('said_no_with_current_partner_then_lifetime_no',target&(f19==2)),
    ],n)
    route_rows=[]
    for label in ['said_no_with_current_partner_then_lifetime_no','no_current_partner_or_f19_skipped']:
        dom=target&(route==label)
        for category,mask in [('reported_prior',pre),('same_age_ambiguous',same),
                              ('reported_later',post),('vaginal_yes_undated',adult_yes_undated),
                              ('vaginal_status_missing',adult_unknown)]:
            route_rows.append({'route':label,'chronology':category,
                               **design_rate(dom,mask,w,reps)})
    pd.DataFrame(route_rows).to_csv(out/'route_by_chronology.csv',index=False,float_format='%.12g')
    # Group by age at Year15 interview; 14, 15, 16+ in completed years.
    bins=[('14_or_younger',target&(months15<180)),
          ('15',target&(months15>=180)&(months15<192)),
          ('16_or_older',target&(months15>=192)&np.isfinite(months15))]
    age_rows=[]
    for label,dom in bins:
        for category,mask in [('reported_prior',pre),('same_age_ambiguous',same),
                              ('reported_later',post)]:
            age_rows.append({'age_at_y15':label,'chronology':category,
                             **design_rate(dom,mask,w,reps)})
    pd.DataFrame(age_rows).to_csv(out/'y15_age_by_chronology.csv',index=False,float_format='%.12g')
    # Debut age minus completed age at adolescent interview. Stratify by severity.
    delta=first-teen_completed
    severity=[('at_least_two_years_earlier',pre&(delta<=-2)),
              ('one_completed_year_earlier',pre&(delta==-1)),
              ('same_completed_year',same),
              ('one_completed_year_later',post&(delta==1)),
              ('two_completed_years_later',post&(delta==2)),
              ('three_or_more_years_later',post&(delta>=3))]
    sev_rows=[]
    for label,mask in severity:
        sev_rows.append({'age_first_minus_completed_age_at_y15':label,
                         **design_rate(target,mask,w,reps)})
    pd.DataFrame(sev_rows).to_csv(out/'chronology_severity.csv',index=False,float_format='%.12g')
    # Checks that distinguish a true inconsistent report from an invalid questionnaire skip.
    flags={
        'y15_no_explicit_f26_lifetime_no':target&(f26==2),
        'male_f19_yes_but_f26_lifetime_no':male&(w>0)&(f19==1)&(f26==2),
        'y15_no_with_f19_current_partner_no':target&(f19==2),
        'y15_no_with_f19_skipped_or_unknown':target&~np.isin(f19,[1.,2.]),
        'adult_any_no_but_vaginal_yes':male&contradiction_e58,
        'adult_vaginal_yes_but_debut_age_missing':adult_yes_undated,
        'adult_vaginal_yes_and_debut_after_interview_age':target&(vaginal==1)&np.isfinite(first)&np.isfinite(months22)&(first>np.floor(months22/12)),
        'y15_yes_but_adult_any_no':year15_teen_yes&y22_any_no,
    }
    # Y15 first intercourse dates should not be populated for an explicit F26=2 respondent.
    # F20: with current partner; F30: first intercourse ever under the applicable route.
    for fld in ['k6f20','k6f30']:
        if fld in d:
            flags[f'y15_no_but_{fld}_valid_event_year']=target&(v[fld]>=2000)&(v[fld]<=2020)
    for fld in ['k6f21','k6f31']:
        if fld in d:
            flags[f'y15_no_but_{fld}_valid_event_age']=target&(v[fld]>=5)&(v[fld]<=18)
    audit=[]
    for label,mask in flags.items():
        dom=(year15_teen_yes if label=='y15_yes_but_adult_any_no' else
             male&(w>0) if label in ['adult_any_no_but_vaginal_yes','male_f19_yes_but_f26_lifetime_no'] else target)
        audit.append({'check':label,'available':True,**design_rate(dom,mask,w,reps)})
    for fld in ['k6f20','k6f30','k6f21','k6f31']:
        if fld not in d:audit.append({'check':f'optional_{fld}_unavailable','available':False})
    pd.DataFrame(audit).to_csv(out/'routing_quality_checks.csv',index=False,float_format='%.12g')
    # Full sample domain sensitivity: drop contradictory histories from adolescent negative target.
    # This scenario changes eligibility and is NOT unbiased correction.
    corrected_dom=target&~pre
    drows=[]
    drows.append({'scenario':'exclude_definite_prior_from_initial_no_domain',
                  'note':'Post hoc eligibility redefinition; not preferred estimate',
                  **design_rate(corrected_dom,post,w,reps)})
    drows.append({'scenario':'original_target_confirmed_after',
                  'note':'Unaltered Year15-negative target',**design_rate(target,post,w,reps)})
    pd.DataFrame(drows).to_csv(out/'denominator_sensitivity.csv',index=False,float_format='%.12g')
    metadata={
        'study':'FFCWS Y15-Y22 forensic chronology and routing audit',
        'respondent_level_exported':False,
        'microdata_input_basename':datafile.name,
        'records_read':int(n),
        'target_n':int(target.sum()),
        'adult_vaginal_valid_n':int((target&np.isfinite(vaginal)).sum()),
        'adult_vaginal_yes_n':int((target&(vaginal==1)).sum()),
        'debut_age_valid_n':int(both.sum()),
        'definitely_before_n':int(pre.sum()),
        'same_completed_age_n':int(same.sum()),
        'definitely_after_n':int(post.sum()),
        'available_optional_variables':[x for x in OPTIONAL if x in d],
        'variance':'33 age15-national jackknife replicate weights; MSE multiplier 1; 1.96 normal CI',
        'privacy':'Suppressed positive subgroup cells under ten; only aggregates saved',
        'interpretation':'Adult recall ages are completed integer years; same age is ambiguous; earlier ages contradict Year15 lifetime no',
        'limitations':[
            'Original initial-no sample selection and adult recall are not independently validated',
            'Cannot distinguish false baseline no from adult retrospective age error',
            'No exact adult calendar date of debut for k7e60; same-age direction is intrinsically indeterminate',
            'No inference to respondents without Year15 data or later birth cohorts',
            'FFCWS vaginal sex does not specify lifetime female partner sex, unlike male NSFG definition',
            'Classification envelopes assume the retrospective integer ages represent true timing; not sharp bounds under unrestricted measurement error',
        ],
        'outputs':[x.name for x in sorted(out.glob('*.csv'))]+['forensic_metadata.json']
    }
    (out/'forensic_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print('Forensic audit completed. Only privacy-screened aggregate outputs:',out)
    print('Year15-negative weighted target:',int(target.sum()),'; age-order PRE/SAME/POST:',int(pre.sum()),int(same.sum()),int(post.sum()))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--allwaves',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    p.add_argument('--strict',action='store_true',help='Stop if prior aggregate counts not reproduced')
    a=p.parse_args()
    run(a.allwaves,a.out,a.strict)
