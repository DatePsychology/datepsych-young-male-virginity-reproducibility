# Independent replication and cross-survey validation: adolescent sexual initiation in the United States, 2011–2025

**Analysis date:** November 23, 2026  
**Evidence:** all eight national Youth Risk Behavior Survey (YRBS) microdata waves (2011, 2013, 2015, 2017, 2019, 2021, 2023, 2025); NSFG male public-use waves 2011–2013, 2013–2015, 2015–2017, 2017–2019 and 2022–2023. All supplied by the user.  
**Status:** completed independent analysis of prevalence, standardization, missing-data sensitivity and an external survey cross-check. Not a causal study.

## Executive conclusion

- The survey-weighted fraction of U.S. high-school **boys** reporting ever having had sexual intercourse decreased from **49.20% in 2011** (95% stratified-PSU CI 46.60–51.80) to **29.71% in 2025** (27.43–32.11). The approximate independent-wave contrast is **−19.48 percentage points** (95% CI −22.93 to −16.03; p < 0.001).
- The decline predates COVID-19: **49.20% in 2011 to 39.23% in 2019** (−9.97 points; 95% CI −14.20 to −5.74). A separate **household-based NSFG** analysis of **all male respondents aged 15–17**, where the outcome is ever vaginal intercourse *with a female*, decreases from **34.42% in 2011–13** to **23.20% in 2017–19**, −11.22 pp (approx. 95% CI −17.85 to −4.59). This is **directional corroboration, not identical-measure replication**.
- The striking 2019-to-2021 fall among schoolboys is only partly age-composition driven: observed **−9.97 pp**, age-standardized to the 2019 male age distribution **−6.74 pp** (95% CI −10.69 to −2.78; p ≈ 0.0011). The result corroborates the specific age-composition concern identified in Santelli et al. (2025).
- For 2023–25 the **−2.44 pp** raw decline is **not** statistically established (95% CI −5.72 to +0.83; p ≈ 0.142). Age-standardized −2.41 pp (CI −5.42 to +0.60, p ≈ 0.116).
- Item nonresponse is substantial and fluctuating. Among male records it was **8.2% unweighted** in 2011, **20.6%** in 2019, **31.4%** in 2021, **20.2%** in 2023, and **18.5%** in 2025. The *survey-weighted* corresponding proportions were 7.3%, 15.6%, 15.7%, 14.5% and 11.1%. The 2011/2025 item-missing extreme-case prevalence bounds do not overlap (2011: 45.6–52.9%, 2025: 26.4–37.5%), **conditional on sampled male student respondents**. These bounds CANNOT address selection of sampled schools or students who never responded.
- Overall national YRBS response fell from about **71% in 2011** to **30.6% in 2025** (official user guides). The latter has a school participation rate of 47%, so unobserved school/student selection remains a serious potential source of bias, not fixed by item-missing bounds or design-adjusted CIs.
- An observed decline in *ever having had intercourse* among adolescents does **not** quantify sexlessness or virginity among men aged 18–30; that adult-cohort claim needs independent adult follow-up or bridge data.

## 1. Outcome and survey design

YRBS primary indicator: original single item **“Have you ever had sexual intercourse?”**; `Q60` (2011, 2015), `Q59` (2013, 2017), `Q58` (2019), `Q57` (2021), `Q56` (2023), `Q54` (2025), with `1=Yes`, `2=No`, blanks missing. For all eight years the original item was verified against corresponding `QN` derived binary variables: they matched on **every** survey record. `Q2=2` denotes male. No assumption about sexual orientation was imposed.

Each wave uses its own `WEIGHT`, masked `STRATUM` and `PSU` fields. The estimator uses weighted ratio means with Taylor linearization of **all primary-sampling units in the survey design**, including PSUs having zero observations in the target male domain. Confidence limits use logit-transformed 95% intervals with t critical values and degrees of freedom equal to the number of sampled PSUs minus strata. Differences between waves use independent-wave variance addition and Satterthwaite degrees of freedom. This treats survey waves as independent and cannot correct unknown design correlations between waves. The available weights are taken as fixed; uncertainty from estimating/calibrating weights is not modeled.

A separate rescaled, stratified PSU bootstrap of 2,000 replicates for 2011, 2019, 2021, 2023, and 2025 corroborates the Taylor SEs: bootstrap/Taylor ratios ranged from approximately 1.006 to 1.031. This confirms **computational consistency of our variance implementation**, not an external Stata/R verification or relief from survey nonresponse bias.

### Main wave-specific estimates (boys reporting ever sexual intercourse)

| YRBS year | Valid male n | Weighted estimate % | 95% CI % |
|---|---:|---:|---:|
| 2011 | 7,032 | 49.20 | 46.60–51.80 |
| 2013 | 6,512 | 47.48 | 44.26–50.72 |
| 2015 | 6,840 | 43.20 | 39.44–47.04 |
| 2017 | 6,221 | 41.41 | 38.61–44.27 |
| 2019 | 5,275 | 39.23 | 35.88–42.69 |
| 2021 | 6,051 | 29.26 | 26.88–31.77 |
| 2023 | 8,029 | 32.16 | 29.86–34.55 |
| 2025 | 4,431 | 29.71 | 27.43–32.11 |

### Key comparisons

| Comparison | Raw delta (pp) | Approx. 95% CI pp | Two-sided p |
|---|---:|---:|---:|
| 2011 to 2019 | −9.97 | −14.20 to −5.74 | 0.000012 |
| 2011 to 2025 | −19.48 | −22.93 to −16.03 | < 0.000001 |
| 2019 to 2021 | −9.97 | −14.10 to −5.83 | 0.000009 |
| 2019 to 2025 | −9.52 | −13.59 to −5.44 | 0.000016 |
| 2023 to 2025 | −2.44 | −5.72 to +0.83 | 0.142 |

## 2. Standardization and detailed trends

Separate age and grade direct standardization used the weighted male distribution **among 2019 valid responders** as a fixed standard. Age standardization includes original YRBS age codes 3, 4, 5, 6, 7 (ages 14, 15, 16, 17, and 18+). Grade standardization includes grades 9–12. The standard distributions are treated as fixed when calculating within-wave CIs; thus uncertainty from the 2019 estimated standard is not fully propagated. The standardized wave estimates and comparisons are sensitivity analyses, not a fully modeled joint age-by-grade adjustment.

| Year | Unadjusted % | Age-standardized % | Grade-standardized % |
|---|---:|---:|---:|
| 2011 | 49.20 | 48.74 | 49.32 |
| 2013 | 47.48 | 45.87 | 47.49 |
| 2015 | 43.20 | 42.24 | 43.14 |
| 2017 | 41.41 | 40.73 | 41.48 |
| 2019 | 39.23 | 39.01 | 39.21 |
| 2021 | 29.26 | 32.27 | 29.11 |
| 2023 | 32.16 | 32.19 | 31.85 |
| 2025 | 29.71 | 29.78 | 29.74 |

The 2021 age-composition shift can be seen directly: weighted fraction of male valid respondents age 14 rose from 11.5% in 2019 to 19.3% in 2021, while the fraction age 18+ fell from 14.1% to 6.7%. Standardization removes approximately 3.2 percentage points of the apparent 10-point drop.

Prespecified four age-standardized comparisons were assessed with Holm correction (see `prespecified_holm_tests.csv`): 2011–25, 2019–21, 2019–25 remain significant; 2023–25 does not. The remaining full battery of subgroups in the CSV is exploratory and should not be treated as confirmatory after multiple testing.

## 3. Survey item nonresponse, worst-case and model sensitivity

The `yrbs_missingness_sensitivity.csv` includes both weighted and unweighted item-nonresponse fractions, **extreme-case bounds**, and five odds-ratio MNAR scenarios. Extreme-case bounds use all sampled male respondents with valid design weight/stratum/PSU: treating every missing answer as `no` yields the lower bound; treating every missing answer as `yes` yields the upper bound. For example, 2011 45.63–52.88% and 2025 26.41–37.53%. These are algebraic bounds for sampled records only, not inferential population CIs.

A second analysis fits survey-weighted age + grade additive logistic regression models among observed boys, predicts expected probabilities for boys whose answer is missing (MAR conditional on measured age and grade), and shifts the missing cases' predicted odds by 0.5 or 2 (sensitivity to a nonignorable mechanism). These are **illustrative sensitivity estimates, without confidence intervals**, not evidence that either MAR or the chosen MNAR odds ratios reflect the real data process.

| Year | Complete-case % | Age/grade-MAR % | MNAR OR 0.5 % | MNAR OR 2 % |
|---|---:|---:|---:|---:|
| 2011 | 49.20 | 49.12 | 47.99 | 50.28 |
| 2019 | 39.23 | 39.35 | 37.15 | 41.81 |
| 2021 | 29.26 | 29.26 | 27.48 | 31.52 |
| 2023 | 32.16 | 32.02 | 30.27 | 34.20 |
| 2025 | 29.71 | 29.67 | 28.39 | 31.29 |

**Most important missingness limitation:** questionnaire omission at some schools and no participation by other schools/students are not individually identifiable from the provided male records; the former may make MAR untenable and the latter is wholly outside item-nonresponse bounds. Survey response decreased from 71% in 2011 to 30.6% in 2025, which may create selection that weights cannot eliminate. Thus design CIs and complete-case trend tests are not complete measures of total uncertainty about the true population.

## 4. Independent NSFG comparison: men aged 15–17

A direct independent calculation from the NSFG male files shows the following estimates of **ever having had vaginal intercourse with a female**, a different construct from YRBS:

| NSFG wave | Valid n age 15–17 | % ever vaginal intercourse with female | 95% CI |
|---|---:|---:|---:|
| 2011–2013 | 650 | 34.42 | 29.57–39.62 |
| 2013–2015 | 624 | 28.46 | 24.33–32.98 |
| 2015–2017 | 517 | 23.07 | 17.52–29.73 |
| 2017–2019 | 595 | 23.20 | 18.97–28.04 |
| 2022–2023 | 393 | 21.22 | 16.82–26.39 |

Across the **pre-2020** surveys, the change is −11.22 pp from the first to last historical NSFG wave (rough independent-wave 95% CI −17.85 to −4.59; p ~ 0.002). The direction agrees with the separate YRBS boys 15–17 decline of −9.83 pp (2011–2019; CI −14.81 to −4.85). The age range is harmonized, but **the populations and behaviors are not**: NSFG includes people not attending high school and specifically requires intercourse with a female, whereas YRBS samples school attendees and does not specify the partner's sex in its item. NSFG 2022–23 is further subject to its own severe survey redesign/low response issues, so comparisons across that break are exploratory.

The observed 2011–2019 declines in both the independent series are stronger support for a real historical adolescent shift than either separately. This does NOT independently confirm an NSFG-specific increase in lifetime intercourse inexperience among men aged 18–29 or 25–30 after 2020. Only adult follow-up with stable measures could do so.

## 5. Interpretation for a methodological critique of Date Psychology

1. **Supported:** A general tendency toward later sexual initiation, certainly among U.S. high-school boys as sampled by the YRBS, is not simply a statistical fiction. The decline predates COVID-19 and is directionally supported by pre-2020 NSFG male adolescent estimates.
2. **Not supported:** The precise magnitude of any rise in *lifetime virginity* among all young adult men, or how many of today's high-school boys remain virgins by age 25. Neither YRBS nor past-year GSS sexlessness estimates identify these trajectories.
3. **Important correction:** Male students' 2021 YRBS age structure explains a substantial fraction of the apparent 2019–2021 fall; the remaining age-adjusted decrease is not zero. One cannot attribute the full apparent 10-point change to either age composition or behavior.
4. **Recent uncertainty:** No significant difference between the observed 2023 and 2025 male rates; do not describe the two points as a newly established acceleration. The severe decline in school participation and changes in survey administration are unquantified threats to causal/historical interpretation.
5. **Missingness:** Observed-item imputation using plausible age/grade MNAR scenarios does not undo the long-term decline, but selection into the survey of schools/students is much more serious and is not addressed by these estimates.
6. **No causal inference:** These repeated cross-sectional trends do not explain *why* intercourse experience fell, or establish that alcohol, video games, dating markets, or social networks caused it.

## 6. Independent numerical validation

- All eight raw question binary codes agree exactly with the CDC-provided `QN` derived variants (number of discrepant records: zero).
- Unadjusted weighted male prevalence reproduces independently published CDC results for 2015–2023 to rounding.
- A separate 2,000-replicate, stratified rescaled PSU bootstrap reproduces linearized SE magnitudes to within 3.2% for five key years; see `independent_bootstrap_variance_check.csv`.
- `input_SHA256.csv` identifies exact inputs without redistributing individual records.

## Sources and qualifications

Original inputs are the user-supplied CDC public-use datasets with SAS import and format programs for each year and NSFG data/dictionaries. Technical documentation is included with the uploaded files but not redistributed in this reproducibility archive.

- CDC National YRBS data: https://www.cdc.gov/yrbs/data/national-yrbs-datasets-documentation.html
- CDC 2025 user guide: https://www.cdc.gov/yrbs/files/2025/2025-YRBS-Data-Users-Guide-Final.pdf
- CDC 2025 methods and 30.6% response rate: https://pmc.ncbi.nlm.nih.gov/articles/PMC13660954/
- CDC 2023 methods: https://www.cdc.gov/mmwr/volumes/73/su/su7304a1.htm
- Santelli et al. (2025) age/missingness survey audit: https://doi.org/10.1007/s13178-025-01223-3
- Lindberg et al. (2021), differences between YRBS and NSFG: https://doi.org/10.1371/journal.pone.0253262

**Residual limitations:** public-use masked design; assumption of independent survey waves; no explicit finite-population corrections; treated 2019 reference distribution as fixed; no statistical correction for school/nonparticipant selection; dichotomous respondent sex only, rather than gender identity; nonidentical item constructs and frames across YRBS and NSFG; uncertain comparability of 2021 and subsequent survey administration. The presence of design-adjusted CIs does not reduce these threats to validity.
