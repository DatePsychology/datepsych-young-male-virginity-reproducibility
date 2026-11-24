import os,re,glob,collections,pandas as pd,numpy as np
src='/mnt/data/yrbs_independent_replication/source'
files={2011:('yrbs2011.dat','YRBS_2011_SAS_Input_Program.sas','Q60'),2013:('yrbs2013.dat','YRBS_2013_SAS_Input_Program.sas','Q59'),2015:('yrbs2015.dat','YRBS_2015_SAS_Input_Program.sas','Q60'),2017:('XXH2017_YRBS_Data.dat','2017XXH_SAS_Input_Program.sas','Q59'),2019:('XXH2019_YRBS_Data.dat','2019XXH-SAS-Input-Program.sas','Q58'),2021:('XXH2021_YRBS_Data.dat','2021XXH-SAS-Input-Program.sas','Q57'),2023:('XXH2023_YRBS_Data.dat','2023XXH-SAS-Input-Program.sas','Q56'),2025:('XXH2025_YRBS_Data.dat','2025XXH-SAS-Input-Program.sas','Q54')}

def pos(t,v):
 p=re.search(r'(?m)^\s*@\s*(\d+)\s+'+v+r'\s+\$?([0-9]+)(?:\.([0-9]+))?\s*\.',t,re.I)
 if p:return int(p[1])-1,int(p[2])
 p=re.search(r'(?m)^\s*'+v+r'\s+\$?\s*(\d+)-(\d+)\b',t,re.I)
 if p:return int(p[1])-1,int(p[2])-int(p[1])+1
 raise Exception((v,t[:400]))

def load(yr):
 dat,sas,ever=files[yr]
 t=open(os.path.join(src,sas),encoding='latin1').read()
 cols=['Q1','Q2','Q3',ever,'QN'+ever[1:],'WEIGHT','STRATUM','PSU']
 mapping={v:pos(t,v) for v in cols}
 lines=open(os.path.join(src,dat),'rb').read().splitlines()
 coldata={v: [l[at:at+length].strip().decode('ascii','replace') for l in lines] for v,(at,length) in mapping.items()}
 d=pd.DataFrame(coldata)
 for v in d: d[v]=pd.to_numeric(d[v], errors='coerce')
 d=d.rename(columns={ever:'everraw','QN'+ever[1:]:'everderived','Q1':'agecode','Q2':'sexcode','Q3':'gradecode','WEIGHT':'weight','STRATUM':'stratum','PSU':'psu'})
 d['year']=yr
 return d,mapping
if __name__=='__main__':
 for year in files:
  d,p=load(year)
  z=d[d.sexcode==2]
  print('\n',year,'positions',p,'n=',len(d),'male n',len(z),'PSU',d.groupby('stratum').psu.nunique().describe().to_dict())
  print('q',d.everraw.value_counts(dropna=False).to_dict(),'derived',d.everderived.value_counts(dropna=False).to_dict())
  print('male q',z.everraw.value_counts(dropna=False).to_dict(),'weighted male ever %', round(np.average((z.loc[z.everraw.isin([1,2]),'everraw']==1).astype(float),weights=z.loc[z.everraw.isin([1,2]),'weight'])*100,2))
  print('male missing % unweighted',round(z.everraw.isna().mean()*100,2),'agecodes',z.agecode.value_counts().sort_index().to_dict())
