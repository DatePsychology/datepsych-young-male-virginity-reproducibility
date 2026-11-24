# FFCWS Year15 → Year22: narrow robustness audit (2026-11-24)

## Status

**Code executed on synthetic data only.** The actual restricted/public-use ICPSR FFCWS microdata were not transmitted to this environment; only the earlier aggregate results were available here. Reproduce the estimates locally using ICPSR DS1 `31622-0001-Data.dta`. The researcher may share **aggregate output files**, subject to the ICPSR agreement. Never upload the `.dta` file, any row-level extract, predictions, or respondent identifiers.

The prior analysis showed 80.0719% Year22-weighted (SE .0359687), 80.3283% Year15 complete-case (SE .0381265), 80.5683% IPW (SE .0350846), and 80.4732% AIPW (SE .0364230). Its *Year15 national-weight-frame*, unadjusted missing-outcome bounds were **62.0573% to 84.8027%**. These are conditional on surviving to Year15 with a valid intercourse report and national weight; they do not address Year15 nonresponse. The new study targets *influence, modeling, and precision* without changing this boundary.

## Windows PowerShell commands (Python 3.12)

1. Extract `FFCWS_Weight_Model_Robustness_2026.zip`, open PowerShell in that folder.
2. Install dependencies:

   ```powershell
   py -3.12 -m pip install -r requirements.txt
   ```

3. Confirm successful execution with fabricated test data only:

   ```powershell
   py -3.12 test_robustness_synthetic.py
   ```

   Expected: `Synthetic regression tests passed (13 variants, independent optimizer, two sharp bounds).`

4. Run the local analysis, replacing the `.dta` path with the actual path on your computer:

   ```powershell
   py -3.12 robustness_audit.py --allwaves "C:\Research\ICPSR_31622\DS0001\31622-0001-Data.dta" --out "C:\Users\Me\Downloads\FFCWS-Weight-Robustness-Results" --strict
   ```

   It prints each specification and its design-informed standard error. There are 13 specifications × 33 jackknife refits, plus independent optimizer checks, so the analysis may involve several hundred regression fits. No data are sent to any server. The output folder is created automatically.

5. Compress **only the resulting aggregate output folder** and upload the ZIP for a methodological interpretation. The following eight files are expected:

   - `model_variants.csv` — 13 model scenarios, weighted estimates, 33-replicate SEs, and concentration metrics.
   - `jackknife_ratio_crosscheck.csv` — independent, direct weighted-ratio and SE checks for Year15/Year22 reference estimators.
   - `independent_solver_check.csv` — original-style scikit-learn vs separately implemented SciPy penalized logistic IPW, both with 33-replicate SEs.
   - `teen_predictor_availability.csv` — which Year15 enrichment variables are present and have usable variation.
   - `response_calibration.csv` — aggregate propensity-prediction calibration in five bins (omits bins smaller than 15).
   - `original_frame_bounds.csv` — independent algebraic Year15-frame identification bounds, **not** uncertainty intervals.
   - `audit_metadata.json` — metadata and tested features, **no microdata**.

   The listed files are **six CSVs and one JSON**. This exact listing supersedes any printed file count.

## Prespecified model specifications

The *same Year15-weighted male baseline-noninitiator target frame* and the *same Year22 any-sex outcome* are used for every model. No outcome definition is switched or optimized.

| Specification | Purpose |
|---|---|
| `baseline_ipw` | Reference IPW model, C=1, propensity clipping 0.02–0.98 |
| `baseline_aipw` | Reference augmented IPW |
| `parsimonious_ipw` | Drop baseline relationship and poverty features |
| `enriched_ipw` | Add validated Year15 behavioral/psychosocial variables |
| `enriched_aipw` | Augmented IPW with added Year15 variables |
| `enriched_weak_ridge` | Less regularization (C=10) |
| `enriched_strong_ridge` | More regularization (C=0.1) |
| `baseline_clip_05` | Constrain propensity to 0.05–0.95 |
| `baseline_clip_10` | Constrain propensity to 0.10–0.90 |
| `baseline_ipw_total_cap_99` | Winsorize combined full analysis weights at 99th percentile |
| `baseline_ipw_total_cap_95` | Winsorize combined full analysis weights at 95th percentile |
| `baseline_ipw_response_cap_95` | Winsorize *response inflation factors only* at 95th percentile |
| `baseline_drop_highest_1pct` | Exclude combined weights above 99th percentile as influence stress test |

Weight-trimmed and exclusion estimates **change the weighting target** and are sensitivity diagnostics, not replacements for the primary estimator. All percentiles, refits, and caps are recomputed within each jackknife replicate. The published FFCWS Year15 random-group jackknife replicate weights use a variance multiplier of 1 and mean-squared-error centering.

The enriched predictors are limited to five verified Year15 questionnaire items, each optional if not present in the distributed file: `k6d40` (ever smoked whole cigarette), `k6d48` (alcohol more than twice without parents), `k6f63` (ever tried marijuana), `k6d2b` (self-report 'love life'), and `k6d61c` (shoplifting item). These are **not** proven causal adjustment variables. Negative special codes are missing categories, not zeroes. The availability report records what was used; do not assume each is present or has valid coverage.

**Independent verification:** Direct NumPy weighted ratios and 33-replicate SEs check the reference estimators; separately written SciPy L-BFGS-B logistic optimization refits the baseline response model for each replicate and is compared against scikit-learn. This is a code and numerical cross-check, not an independent dataset or validation of missing-at-random assumptions. An optional `independent_stata_check.do` performs the two unadjusted weighted survey means and SEs using official `svyset` notation if you have Stata. It is not required.

## Interpretation decision rules (set before viewing new results)

- **Reassuring**: regularization/covariate/propensity changes move IPW/AIPW estimates by no more than about **2 percentage points**, 95th-percentile total-weight capping moves the estimate by no more than about **5 percentage points**, no serious calibration failures, and independent solver estimates agree within **0.3 percentage points** in point and jackknife SE.
- **Model-sensitive**: changes exceed those thresholds, model refits fail, significant weight leverage, pronounced calibration errors, or the enriched model excludes many important people through missing values (this script retains missingness as categories to avoid silently dropping them).
- **Main qualitative finding**: model shifts cannot change the original Year15-frame *sharp bounds*: when every unobserved Year22 outcome in that frame is coded zero, the weighted rate remains about **62.06%**, above half. This is conditional on measured Year15 status and national-weight eligibility and not valid for everyone born in the underlying cities.

The cutoffs above are editorial decision criteria, **not** inferential thresholds or proof of equivalence. Overlapping CIs across models do not validate model specification. A cap may appear reassuring because it changes the estimand; its value is as an influence check only.

## Known limitations

1. The Year15 and Year22 national weights condition on different waves' respondents and no dedicated all-wave longitudinal weights exist. Differences among their estimates reflect both weighting and sample-target issues.
2. Sex was recorded at birth (`cm1bsex == 1`) and the outcome is `k7e58` *ever had sex*; Year15 intercourse routing differs and Year22 does not mean precisely the 22nd birthday.
3. The extra Year15 predictors were selected *because they predate the outcome*, not because they fully account for attrition. More covariates can introduce instability and don't guarantee less bias.
4. The model's regularization penalty and StandardScaler are implemented in standard penalized logistic regression. Both implementations are compared but cannot resolve systematic selection on unobserved traits.
5. Several weighting variants are exploratory stress tests, not independent estimators of a causal effect. The sampling variance uses the 33 supplied replicate weights but may be approximate for nonlinear and trimmed estimators. The independent Stata check validates only unadjusted survey means.
6. All results concern one urban birth cohort (1998–2000); no inference about today's cohort trends or the NSFG post-redesign discontinuity.

## Sources

- [Official FFCWS guide to using wave-specific weights](https://ffcws.princeton.edu/sites/g/files/toruqf4356/files/documents/using_the_fragile_families_weights_waves_1_6_06082026.pdf): explicitly says longitudinal weights are not available and gives `svyset [pweight=...], jkrw(..., multiplier(1)) vce(jack) mse`.
- [Official FFCWS Year15 weight technical note](https://ffcws.princeton.edu/sites/g/files/toruqf4356/files/documents/ff_const_wgtsy15.pdf): national random-group replicate weights use 33 groups.
- [Official FFCWS Year22 weight note](https://ffcws.princeton.edu/sites/g/files/toruqf4356/files/documents/Year_22_Weight_Document_Final_1.pdf).
- [FFCWS Year15 public-use guide](https://ffcws.princeton.edu/sites/g/files/toruqf4356/files/ff_public_guide_15.pdf) (Year15 tobacco, alcohol and drug-use items).
- [Independent paper listing Year15 item names and labels](https://pmc.ncbi.nlm.nih.gov/articles/PMC10037103/).
