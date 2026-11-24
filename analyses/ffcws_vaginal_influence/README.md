# FFCWS vaginal-intercourse weight-influence audit (v1.0.0)

## Scope and data handling
This is the final focused empirical check requested in the review of *Young Male Virginity: Revisiting Date Psychology’s 2023 Conclusions*. It is a local-only program for the same authorized ICPSR 31622 DS0001 all-wave Stata file used in earlier analyses. Do not upload respondent-level records, identifiers, weight vectors, or individual predictions. Run only if your data-use terms permit the local analysis. Review outputs before any sharing and share only aggregate files permitted by those terms. Do not use synthetic-test mode to bypass a real-data mismatch.

## Windows PowerShell
Extract this ZIP into Downloads, preserving its folder structure. Use the Python 3.12 installation that worked in the previous audits (avoid the earlier Python 3.15 dependency-build problem).

```powershell
cd "$HOME\Downloads\FFCWS_Vaginal_Influence_Audit_2026"
py -3.12 -m pip install -r requirements.txt
py -3.12 test_vaginal_influence_synthetic.py
```

Set `$data` to your actual all-wave .dta location (the next example is a placeholder; use the same actual path as for the earlier harmonization/forensic run):

```powershell
$data = "C:\Research\ICPSR_31622\DS0001\31622-0001-Data.dta"
Test-Path -LiteralPath $data
py -3.12 vaginal_influence_audit.py --allwaves "$data" --out "$HOME\Downloads\FFCWS-Vaginal-Influence-Results"
```

`Test-Path` must report `True`. If necessary, change the path or locate the earlier file in File Explorer. Use a new, empty output directory; if a previous run exists, choose another folder. Strict historical validation is on by default. If validation fails, report the error message rather than changing the expected sample or disabling validation. The script accepts .dta or CSV; use the original .dta to reproduce earlier runs.

## Aggregate results to return (subject to the applicable data-use terms)
- `audit_validation.json`
- `vaginal_weight_sensitivity.csv`
- `vaginal_weight_concentration.csv`

No input dataset, respondent identifiers, individual outcomes or probabilities, replicate-specific estimates, thresholds, dropped-case counts or dropped-case outcomes are written. Sensitivity estimates describe the remaining large analytical sample; no small-subgroup outcome is directly reported. The estimates and CIs in the CSV are rounded to 2 decimal percentage points. If your data-use terms disallow sharing any of these, retain them locally and describe the permitted aggregate conclusions instead.

## Estimation and diagnostics
The original outcome coding is imported unchanged from `harmonize_ffcws.py`. The target is male respondents with explicit Year-15 lifetime-no and positive Year-15 national weights. The response indicator is **availability of the harmonized Year-22 vaginal outcome**, not availability of the broader any-sex measure. There are 938 target respondents, 697 observed outcomes, and 514 positive outcomes in the historical run. Year-22 sensitivity uses a separate weighting frame (734 eligible, 697 observed). Historical point estimates and standard errors must match within 0.02 percentage points. The original model metadata lists five usable predictors: mother's age, race/ethnicity, education, relationship with father and poverty category. The candidate Year-15 interview-age predictor was not used in that archived run. The reference covariate builder is unchanged; a different predictor set stops strict execution. Missing indicators and dummy coding follow the original script. The response model is normalized-weight L2 logistic regression, C=1, standardized predictors, and predicted probabilities clipped to [0.02, 0.98].

For each full-sample and replicate-weight fit, compute complete cases, uncapped IPW, survey-only caps, response-factor-only caps, combined-weight caps, and exclusion strictly above the combined-weight 99th/95th percentile. Quantiles are unweighted linear quantiles over positive-weight observed respondents. In IPW survey-only caps, the response-model fit is retained: only the final survey-weight component changes. These specifications isolate mathematical leverage, not alternative fully calibrated weights. For deletion, ties at the threshold are retained; selection is recomputed within each replicate. Replicate weights with zero values contribute no observations. No case-level quantities leave memory. Two original baseline models report Kish ESS and aggregate top 1%/5% weight shares. ESS measures unequal-weight concentration, not the full cluster-design effective sample size.

For every sensitivity estimate, calculate a 33-replicate MSE-centered SE using the existing FFCWS convention (sum of squared deviations), Wald 95% intervals, and paired differences against the relevant untrimmed estimator and the original Year-15 complete-case estimator. In paired contrasts the same replicate supplies both estimates. Year-22 is not paired with Year-15 because its weights represent a different frame. All 33 replicates must be valid. The archived estimator is independently invoked to cross-check the original CC and IPW points and SEs; the new response fit also treats convergence warnings as errors. Wald intervals for adaptive trimming/deletion are exploratory and do not prove an alternative estimator is unbiased. No multiple-testing claim is made.

## Interpretation agreed before the local run
- Changes of approximately 1–2 points across reasonable specifications: reassuring about extreme-weight sensitivity.
- Several-point changes: report quantitative sensitivity.
- More than 5 points after deletion: emphasize influential weights, not a corrected population estimate.
These are descriptive benchmarks, not formal hypothesis tests. The audit does not resolve unmeasured selection, contradictory histories, recall error, or applicability to newer cohorts. The synthetic test log does not supply real empirical results.
