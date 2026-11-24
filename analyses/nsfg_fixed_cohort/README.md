# NSFG adult sexual-initiation transition and fixed-cohort falsification audit

Analytical date: 2026-11-23.

This package contains Python code, aggregate tables, a variance-validation bootstrap and figures computed from user-provided public-use NSFG male microdata. **It does not contain individual respondents' data.**

## Research questions
1. Among men aged 25–29, what fractions had never had heterosexual vaginal intercourse by their 18th, 21st and 25th birthdays? What share of those still inexperienced on their 21st birthday initiated before their 25th?
2. Are survey results for **the same already-passed milestone** consistent when the same approximate birth cohort is sampled in 2017–2019 and 2022–2023?
3. How sensitive are these results to birth-cohort boundaries, sexual-orientation restrictions, and 2022–2023 mode of interview?

## To reproduce

Python >=3.10, `numpy`, `pandas`, `scipy`, `matplotlib`. Install with `pip install -r requirements.txt`.

Place these files in `input/` (or set environment variable `NSFG_DATA_ROOT` to the directory containing them):

- `2011_2013_MaleData.dat` and `2011_2013_MaleSetup.dct`
- `2013_2015_MaleData.dat` and `2013_2015_MaleSetup(1).dct` (or any `2013_2015_MaleSetup*.dct`)
- `2015_2017_MaleData.dat` and `2015_2017_MaleSetup.dct`
- `2017_2019_MaleData.dat` and `2017_2019_MaleSetup(1).dct` (or any `2017_2019_MaleSetup*.dct`)
- `NSFG-2022-2023-MaleRespPUFData.zip`

Run:
```
python analyze.py
python robustness.py
python bootstrap_validation.py
python make_figures.py
python test_results.py
```
Scripts save aggregate outputs in `output/`; they do not modify the source files. `robustness.py` and `bootstrap_validation.py` import `analyze.py`, which automatically recomputes primary tables for transparency. The verification files were produced with `NSFG_DATA_ROOT=/mnt/data` and this script folder at `/mnt/data/nsfg_adult_transition`.

## Estimand
`HADSEX==1` indicates ever experienced heterosexual vaginal intercourse with a woman; `HADSEX==2` indicates no such experience by the survey interview. `VRY1STAG` gives completed age in years at first heterosexual vaginal intercourse, with public-use bottom-coding at age 10 in 2017–2019 and 2022–2023. `never_before_21 = HADSEX==2 OR (HADSEX==1 AND VRY1STAG >=21)` is interpretable among men **aged >=21 at interview**. All other birthday threshold measures use the same principle, including only respondents past the respective age. This is an age milestone, not lifetime sexual inactivity in every sense.

Design estimates use `SEST`/`SECU` and original wave weights (historical NSFG), `VEST`/`VECL` and `WGT2022_2023` (2022–23). Taylor-linearized with-replacement PSU estimates maintain the full survey strata/PSUs in each within-wave domain. Between-wave differences assume independent waves and use Satterthwaite critical values; design overlap is not documented. `bootstrap_validation.csv` independently verifies primary contrasts with 1,600 stratified rescaled-PSU bootstrap replicates (seed 20261123). Birth cohorts are approximate from `interview_year - AGER` and may be one calendar year off for individuals. 2022–2023 interview mode was not randomized; mode-specific final weights do not estimate randomized mode effects.

### Key limits
Retrospective age at first sex recodes changed between 2017–2019 and 2022–2023. Cohort compositions can also change through migration, mortality, participation and population-weight shifts. The historical milestone comparison is a falsification **diagnostic of comparability**, not proof of any single causal source of discordance. The proportion of men that never experience heterosexual vaginal intercourse over their lifetime cannot yet be inferred for the youngest cohorts: many are right-censored. See `REPORT.md`.

Official methods: [CDC 2017–2019 male recode specifications](https://www.cdc.gov/nchs/data/nsfg/NSFG-2017-2019-UG-App3c-MaleRecodeSpecs-508.pdf) and [CDC 2022–2023 male recode specifications](https://www.cdc.gov/nchs/data/nsfg/recodespecs/2022-2023-NSFG-Male-RecodeSpecs.pdf).
