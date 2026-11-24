# Narrow robustness audit: what the existing aggregate evidence actually proves

**Prepared:** 2026-11-24. **Stage:** Source-code audit and aggregate-result verification completed; new 13-specification microdata robustness grid awaits the authorized local run.

## Reference estimators (supplied aggregate data)

| Approach | Estimate | Jackknife SE | 95% normal CI |
|---|---:|---:|---:|
| Year22-weighted complete case, n=701 | 80.071903% | 3.596869 pp | 73.0220–87.1218% |
| Year15-weighted complete case, n=701 | 80.328317% | 3.812653 pp | 72.8555–87.8011% |
| Year15 inverse-probability weighted | 80.568345% | 3.508465 pp | 73.6918–87.4449% |
| Year15 augmented IPW | 80.473157% | 3.642305 pp | 73.3342–87.6121% |

All four estimates share observed Year22 outcomes; the similarity does not prove missingness at random. The total point-estimate spread is **0.4964 percentage points**.

**Separate, sharp full-frame missing-outcome bounds**: 62.057281%–84.802729%. This is the Year15-national-weight-domain population of **938** boys with valid negative Year15 status, of whom **701** have observed Year22 any-sex status. All 237 missing follow-ups coded 'no sex' leaves the lower endpoint above 50%. This bound **does not** cover boys without Year15 interview/weight, questionnaire misclassification, or another birth cohort. It is **not** an estimate of the probability of initiation among the general population.

## Newly identified technical and research issues

1. The Year15-weight and Year22-weight means describe slightly different response-conditioned target populations. The FFCWS weights guide says no longitudinal weights are available and recommends choosing a wave's sampling weights; the Year15-weight frame is sensible for testing follow-up attrition, but is not a magically unbiased longitudinal estimator.
2. The previous IPW model's weight-only Kish ESS was **147.45** from 701 observed respondents, and its largest full adjusted analysis weight was **62.67 times** the median. The script reported 0.43% of response probabilities at the floor/ceiling; trimming the **propensity inverse** alone might do little when the problem is variation in the **original sampling weights**. Accordingly, both full-weight and response-only caps must be tested and clearly labeled separately.
3. The previous code represented categorical baseline factors with indicator variables; one response-model specification and one ridge penalty were used. It gave no calibration, coefficient sensitivity, or enriched-predictor specifications. The new audit adds an a priori model grid and teen measures documented in source questionnaires.
4. The previous jackknife implementation used `sqrt(sum((replicate_estimate - full_estimate)^2))`, matching the FFCWS `multiplier(1) mse` convention. The new audit *independently* implements direct weighted ratios and fits the baseline response model with both scikit-learn and SciPy L-BFGS-B for 33 refits. Agreement on the same data/weights only checks implementation, not representativeness.
5. To avoid changing the outcome or study population mid-investigation, all 13 variants retain `k7e58` ever had sex by the Year22 interview and the 938-person Year15 national-weight-eligible baseline noninitiator target frame. Exact 22nd-birthday vaginal intercourse and more recent cohorts remain out of scope.

## Judgment before seeing new sensitivity results

**Currently supported:** substantial initiation after the Year15 interview. A majority-catch-up conclusion is insensitive to observed Year22 outcome attrition *within the defined Year15-weight frame*, even under worst-case assigned outcomes.

**Provisional:** the numerical estimate of roughly 80% for that Year15 population. Different model specifications, influence of top weights, and remaining unmeasured attrition/selection all still need scrutiny. The new local analysis specifically tests the first two; no model can resolve the third from these data.

## Audit provenance and reproducibility

Source inputs: eight aggregate outputs uploaded by the researcher on 2026-11-24 and the original `ffcws_attrition.py` supplied in the prior analysis package. No respondent-level FFCWS records were available in this environment.

The bundled `test_robustness_synthetic.py` runs 13 prespecified variants and an independently implemented logistic optimizer using only **fabricated** data; it passed locally. The new variants have **not** been executed on actual FFCWS microdata by this assistant. All participant-level results require local execution by the authorized researcher.
