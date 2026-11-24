# GSS–NSFG virginity estimates: independent replication package

**Run completed:** November 23, 2026, on user-provided original public-use respondent data.  
**Research report:** [`REPORT.md`](REPORT.md)  
**Results:** `output/prevalence_all.csv` (352 rows), `output/wave_contrasts.csv` (176 rows), `output/sensitivity_modes_weights.csv`, `output/nsfg_fixed_age_standardized.csv`, `output/gss_sample_coverage.csv`, plus two PNG figures.

### Re-run

1. Install Python 3.10+ and requirements from `requirements.txt`.
2. Place these in `input/`:
   - `GSS_stata.zip` from [NORC](https://gss.norc.org/get-the-data/stata.html) **or** extracted `gss7224_r3a.dta`.
   - `NSFG-2022-2023-MaleRespPUFData.zip` from [CDC](https://www.cdc.gov/nchs/nsfg/documentation/2022-2023.html).
   - Four `2011_2013_MaleData.dat`, `2013_2015_MaleData.dat`, `2015_2017_MaleData.dat`, `2017_2019_MaleData.dat` files and each corresponding `_MaleSetup.dct` file. Dictionaries with the `(1)` filename suffix are also accepted.
3. `python replicate_full.py`
4. `python sensitivity.py`
5. `python test_replication.py`
6. `python make_figures.py`

**No respondent microdata are included in this package.** The `input_hashes.json` provides SHA-256 hashes of the exact archives and historical raw `.dat` files analyzed; verify these against downloaded files.

### Methods

`replicate_full.py` implements stratified cluster linearization for weighted binary domain proportions. All PSUs from the relevant survey wave enter each domain variance. Clusters are centered within strata with the with-replacement `m_h/(m_h-1)` correction. The degrees of freedom equal the total sampled PSUs minus strata, and 95% proportion CIs use a design-t critical value on the logit scale. Wave comparisons assume independent samples and use Satterthwaite t confidence intervals. This is an explicit *approximation* for NSFG multiple-cycle comparisons and does not account for redesigns or changes in reporting mode.

NSFG face-to-face vs web output uses the full 2022–2023 survey weights, treating interview mode as a domain; these are observational diagnostic estimates and should not be promoted as separate representative estimates for the national population. See the detailed cautions in `REPORT.md`.

### QA checks

`test_replication.py` verifies independently against the article's original 2018/2021 GSS point estimates, 2017–2019 NSFG chart estimates, the CDC's 2022–2023 HADSEX frequency, and 2024 GSS missing NUMWOMEN. All tests passed on the supplied files.
