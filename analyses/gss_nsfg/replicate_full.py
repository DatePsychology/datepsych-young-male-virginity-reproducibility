#!/usr/bin/env python3
"""Independent audit of three GSS/NSFG outcomes. Requires user-supplied original microdata.

Primary outcomes: (a) GSS PARTNERS=0 last 12 mo (b) GSS NUMWOMEN=0
female partners since 18 (c) NSFG HADSEX=2 never vaginal intercourse with a female.
This is code written for the attached public-use datasets; no invented observations.
"""
from pathlib import Path
import io,zipfile,re, math, glob, json
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from scipy.stats import t as td

ROOT=Path(__file__).resolve().parent
IN=ROOT/'input';OUT=ROOT/'output';OUT.mkdir(exist_ok=True)
YEARS=[2008,2010,2012,2014,2016,2018,2021,2022,2024]
NSFG=['2011_2013','2013_2015','2015_2017','2017_2019']
GROUPS={'18–19':(18,19),'18–20':(18,20),'18–24':(18,24),'21–24':(21,24),'25–29':(25,29),'25–30':(25,30),'18–29':(18,29),'18–30':(18,30)}

def estimate(frame, outcome, domain, wt='wt',strat='stratum',psu='psu'):
    """With-replacement stratified PSU linearization for weighted mean, domain inference.
    Keep all PSUs in same wave even when no sampled members belong to domain.
    Multiplies strata-specific centered PSU influence by m_h/(m_h-1).
    """
    d=frame.loc[(frame[wt]>0)&frame[wt].notna()&frame[strat].notna()&frame[psu].notna()].copy()
    msk=domain.reindex(d.index).fillna(False)&d[outcome].isin([0,1]); y=d[outcome];n=int(msk.sum());events=int((msk & y.eq(1)).sum())
    if n<1:return None
    w=d[wt]; denom=float(w.loc[msk].sum());p=float((w[msk]*y[msk]).sum()/denom)
    infl=np.where(msk,w*(y.fillna(0)-p)/denom,0)
    group=pd.DataFrame({'s':d[strat].to_numpy(),'u':d[psu].to_numpy(),'lin':infl}).groupby(['s','u'],sort=False).lin.sum()
    var=0.;deg=0;details=[]
    for s,g in group.groupby(level=0):
        a=g.to_numpy();m=len(a)
        if m<2: raise ValueError(f'Singleton design stratum {s}')
        var+=(m/(m-1))*np.sum((a-a.mean())**2); deg+=m-1
        details.append((s,m))
    se=math.sqrt(var);critical=float(td.ppf(.975,deg));
    if p>0 and p<1:
        logse=se/(p*(1-p));lo,hi=expit(logit(p)+np.array([-1,1])*critical*logse)
    else:lo,hi=(np.nan,np.nan)
    return dict(n=n,events=events,estimate_pct=100*p,SE_pp=100*se,ci95_low_pct=100*lo,ci95_high_pct=100*hi,
      wald95_low_pct=100*max(0,p-critical*se),wald95_high_pct=100*min(1,p+critical*se),design_df=deg,
      num_strata=len(details),num_psu=sum(x[1] for x in details),weight_sum=denom)

def get_gss():
    p=IN/'gss7224_r3a.dta';
    if not p.exists():
        z=IN/'GSS_stata.zip'
        with zipfile.ZipFile(z) as f:
            p.write_bytes(f.read('GSS_stata/gss7224_r3a.dta'))
    cols=['year','age','sex','sexornt','numwomen','partners','partners_8822','wtss','wtssnr','wtssps','wtssnrps','vstrat','vpsu']
    d=pd.read_stata(p,columns=cols,convert_categoricals=False)
    d=d.loc[d.year.isin(YEARS)].copy()
    for c in cols:d[c]=pd.to_numeric(d[c],errors='coerce')
    d['wt']=d.wtssnrps; d['stratum']=d.vstrat;d['psu']=d.vpsu
    d['male']=d.sex.eq(1);d['straight']=d.sexornt.eq(3)
    # NUMWOMEN unusual qualitative codes: 991=1+ unknown; 994=several;
    # 995=many/lots (all imply >=1). Other 990-997 responses are ambiguous
    # (e.g. 993=garbled, 997=refused) and excluded as missing.
    # NUMWOMEN was not administered in 2024.
    valid=((d.numwomen>=0)&(d.numwomen<=989))|d.numwomen.isin([991,994,995])
    d['zero_female_since18']=np.where(valid,d.numwomen.eq(0).astype(float),np.nan)
    # PARTNERS is the harmonized all-year recode, including 2024; 9 means 1+ (unspecified).
    d['zero_partners_12mo']=np.where(d.partners.isin([0,1,2,3,4,5,6,9]),d.partners.eq(0).astype(float),np.nan)
    return d

def fields_from_stata_dictionary(fname,needed):
    t=Path(fname).read_text(encoding='latin1')
    pat=re.compile(r'_column\s*\(\s*(\d+)\s*\)\s+(\w+)\s+(\w+)\s+(%[0-9]+[A-Za-z])',re.I)
    fields={name.upper():(int(pos),typ.lower(),fmt) for pos,typ,name,fmt in pat.findall(t)}
    assert set(needed).issubset(fields),f'{fname} missing {set(needed)-set(fields)}'
    cs=[]
    for k in needed:
        pos,typ,fmt=fields[k];width=int(re.search(r'(\d+)',fmt)[1]);cs.append((pos-1,pos-1+width))
    return cs

def get_old_nsfg(y):
    candidates=glob.glob(str(IN/f'{y}_MaleSetup*.dct'))
    assert len(candidates)==1,(y,candidates)
    dct=candidates[0];col=['AGER','HADSEX','SEX12MO',f'WGT{y}','SEST','SECU']
    if y in ['2015_2017','2017_2019']:col+=['ORIENT_A','ORIENT_B']
    else:col+=['ORIENT']
    cs=fields_from_stata_dictionary(dct,col)
    d=pd.read_fwf(IN/f'{y}_MaleData.dat',colspecs=cs,names=col,dtype='str')
    for c in col:d[c]=pd.to_numeric(d[c],errors='coerce')
    d['straight']=d['ORIENT'].eq(1) if 'ORIENT' in d.columns else (d.ORIENT_A.eq(1)|d.ORIENT_B.eq(2))
    d['year']=y.replace('_','–');d['wt']=d[f'WGT{y}'];d['psu']=d.SECU;d['stratum']=d.SEST;d['age']=d.AGER
    d['never_vaginal']=np.where(d.HADSEX.isin([1,2]),d.HADSEX.eq(2).astype(float),np.nan)
    return d

def get_new_nsfg():
    z=IN/'NSFG-2022-2023-MaleRespPUFData.zip'
    with zipfile.ZipFile(z) as f:d=pd.read_csv(io.BytesIO(f.read('NSFG_2022_2023_MaleRespPUFData.csv')),low_memory=False)
    d['year']='2022–2023';d['wt']=d.WGT2022_2023;d['psu']=d.VECL;d['stratum']=d.VEST;d['age']=d.AGER
    d['straight']=d.ORIENT.eq(2)
    d['never_vaginal']=np.where(d.HADSEX.isin([1,2]),d.HADSEX.eq(2).astype(float),np.nan)
    return d

def run():
    results=[];frames={}; d=get_gss();frames['GSS']=d
    print('GSS total 2008+ rows',len(d))
    print('GSS usable NUMWOMEN 2024:',int(d.loc[d.year==2024,'zero_female_since18'].notna().sum()))
    for year in YEARS:
        x=d.loc[d.year==year];
        for o in ['zero_partners_12mo','zero_female_since18']:
            for pop in ['all men','heterosexual men']:
                for age,(lower,upper) in GROUPS.items():
                    domain=x.male & x.age.between(lower,upper)
                    if pop=='heterosexual men':domain&=x.straight
                    est=estimate(x,o,domain)
                    if est: results.append({'dataset':'GSS','wave':str(year),'outcome':o,'population':pop,'age_group':age,**est})
    for y in NSFG:
        x=get_old_nsfg(y);frames[y]=x
        print('NSFG',y,'n',len(x),'design',(x.stratum.nunique(),x.groupby('stratum').psu.nunique().sum()),'18-29',x.age.between(18,29).sum(),'HADSEX',x.HADSEX.value_counts(dropna=False).to_dict())
    frames['2022_2023']=get_new_nsfg();x=frames['2022_2023'];print('NSFG new',len(x),'design',(x.stratum.nunique(),x.groupby('stratum').psu.nunique().sum()))
    for y in NSFG+['2022_2023']:
        x=frames[y];wave=x.year.iloc[0]
        for pop in ['all men','heterosexual men']:
            for age,(lower,upper) in GROUPS.items():
                dom=x.age.between(lower,upper)
                if pop=='heterosexual men':dom&=x.straight
                est=estimate(x,'never_vaginal',dom)
                if est:results.append({'dataset':'NSFG','wave':wave,'outcome':'never_vaginal','population':pop,'age_group':age,**est})
    out=pd.DataFrame(results);out.to_csv(OUT/'prevalence_all.csv',index=False,float_format='%.6f')
    contrast=[]
    cmp=[('GSS','zero_partners_12mo','2014','2018'),('GSS','zero_partners_12mo','2018','2021'),('GSS','zero_partners_12mo','2018','2022'),('GSS','zero_partners_12mo','2018','2024'),('GSS','zero_partners_12mo','2022','2024'),('GSS','zero_female_since18','2014','2018'),('GSS','zero_female_since18','2018','2021'),('GSS','zero_female_since18','2018','2022'),('NSFG','never_vaginal','2011–2013','2017–2019'),('NSFG','never_vaginal','2017–2019','2022–2023'),('NSFG','never_vaginal','2011–2013','2022–2023')]
    for dataset,o,start,end in cmp:
        for pop in ['all men','heterosexual men']:
            for group in GROUPS:
                a=out.loc[(out.dataset==dataset)&(out.outcome==o)&(out.wave==start)&(out.population==pop)&(out.age_group==group)]
                b=out.loc[(out.dataset==dataset)&(out.outcome==o)&(out.wave==end)&(out.population==pop)&(out.age_group==group)]
                if len(a)!=1 or len(b)!=1:continue
                a,b=a.iloc[0],b.iloc[0];var1=a.SE_pp**2;var2=b.SE_pp**2;se=np.sqrt(var1+var2)
                df=(var1+var2)**2/(var1**2/a.design_df+var2**2/b.design_df) if se>0 else np.nan
                t=b.estimate_pct-a.estimate_pct;p=2*td.sf(abs(t/se),df) if se>0 else np.nan
                c=td.ppf(.975,df)*se if se>0 else np.nan
                contrast.append(dict(dataset=dataset,outcome=o,from_wave=start,to_wave=end,population=pop,age_group=group,delta_pp=t,SE_pp=se,ci95_low_delta_pp=t-c,ci95_high_delta_pp=t+c,p_two_sided=p,df=df))
    contrasts=pd.DataFrame(contrast);contrasts.to_csv(OUT/'wave_contrasts.csv',index=False,float_format='%.6f')
    # Respondent frequencies and sample denominators for key reporting, include nonresponse ascertainment.
    r=[]
    for year in YEARS:
        x=d.loc[(d.year==year)&d.male&d.age.between(18,29)]
        r.append(dict(year=year,all_men_n=len(x),all_men_valid_numwomen=x.zero_female_since18.notna().sum(),all_men_valid_partners=x.zero_partners_12mo.notna().sum(),straight_men_n=int(x.straight.sum()),straight_men_valid_numwomen=int((x.straight&x.zero_female_since18.notna()).sum())))
    pd.DataFrame(r).to_csv(OUT/'gss_sample_coverage.csv',index=False)
    print('Saved',len(out),'prevalence estimates and',len(contrasts),'year contrasts')
    for dataset,oc,pop,age in [('GSS','zero_female_since18','heterosexual men','18–30'),('GSS','zero_partners_12mo','all men','18–29'),('NSFG','never_vaginal','all men','18–29'),('NSFG','never_vaginal','heterosexual men','18–29'),('NSFG','never_vaginal','all men','25–30')]:
        m=out[(out.dataset==dataset)&(out.outcome==oc)&(out.population==pop)&(out.age_group==age)]
        print('\n',dataset,oc,pop,age);print(m[['wave','n','events','estimate_pct','ci95_low_pct','ci95_high_pct','design_df']].to_string(index=False,float_format=lambda v:f'{v:.2f}'))
    return out,contrasts

if __name__=='__main__':run()
