* Optional independent Stata cross-check of UNADJUSTED proportions and SEs.
* Requires a licensed Stata installation. Not required for Python analysis.
* CHANGE THE LOCAL PATH. ICPSR microdata remain on your computer.
clear all
set more off
use "C:\Research\ICPSR_31622\DS0001\31622-0001-Data.dta", clear

* Match reference Python routing; no = yes (1) at Year15 if either question yes,
* no = 0 only when k6f26==2 and k6f19 != 1.
generate byte age15_no = (k6f26 == 2 & k6f19 != 1)
generate byte adult_yes = .
replace adult_yes = 1 if k7e58 == 1
replace adult_yes = 0 if k7e58 == 2

* Year 15 national-weighted complete-case ratio using all positive-weight
* Year 15 records and a subpopulation indicator (rather than dropping domain).
preserve
keep if k6natwt > 0 & k6natwt < .
generate byte domain = (cm1bsex == 1 & age15_no == 1 & adult_yes < .)
svyset [pweight=k6natwt], jkrweight(k6natwt_rep*, multiplier(1)) vce(jack) mse
svy, subpop(domain): mean adult_yes
* Expected point approximately 0.80328317; SE approximately 0.038126533.
restore

* Separate year 22 national-weighted complete-case, different weight universe.
preserve
keep if k7natwt > 0 & k7natwt < .
generate byte domain = (cm1bsex == 1 & age15_no == 1 & adult_yes < .)
svyset [pweight=k7natwt], jkrweight(k7natwt_rep*, multiplier(1)) vce(jack) mse
svy, subpop(domain): mean adult_yes
* Expected point approximately 0.80071903; SE approximately 0.035968688.
restore
