"""Data integrity and known-figure validation; requires original data in ./input/."""
import numpy as np
from replicate_full import get_gss,get_old_nsfg,get_new_nsfg,estimate

g=get_gss()
y=g.loc[(g.year==2018)&g.male&g.straight&g.age.between(18,30)&g.numwomen.notna()]
r=100*np.average(y.numwomen.eq(0),weights=y.wtss)
assert abs(r-24.927)<0.02,('Alexander GSS 2018 24.93',r)
y=g.loc[(g.year==2021)&g.male&g.straight&g.age.between(18,30)&g.numwomen.notna()]
r=100*np.average(y.numwomen.eq(0),weights=y.wtssps)
assert abs(r-16.639)<0.02,('Alexander GSS 2021 16.64',r)
a=get_old_nsfg('2017_2019');r=estimate(a,'never_vaginal',a.straight&a.age.between(18,29))
assert abs(r['estimate_pct']-15.265)<0.05,r
r=estimate(a,'never_vaginal',a.straight&a.age.between(25,30))
assert abs(r['estimate_pct']-3.947)<0.05,r
b=get_new_nsfg();assert len(b)==4371 and b.HADSEX.eq(2).sum()==1009
assert not g.loc[g.year==2024,'zero_female_since18'].notna().any()
# Demonstrate special GSS qualitative codes that nevertheless mean nonzero partner counts.
for n in [991,994,995]:
    test=g.loc[g.numwomen==n,'zero_female_since18']
    assert (test==0).all(),(n,test)
print('PASS: two GSS point-estimate benchmarks, two NSFG benchmarks, CDC 2022–23 codebook count, GSS 2024 nonadministration and 991/994/995 partner coding.')
