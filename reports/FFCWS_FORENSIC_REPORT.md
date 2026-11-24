# Independent aggregate review: FFCWS inconsistent sexual histories

**Review date:** 24 November 2026  
**Input:** Eight aggregate CSV/JSON outputs of the locally executed `forensic_histories.py` analysis, including survey-weighted results. No respondent-level ICPSR records were transferred or reanalysed here.  
**Scope:** Boys reporting no intercourse at the FFCWS Year 15 interview, followed to the Year 22 young-adult interview; public-use, age-15 positive national-weight domain.

## Executive conclusions

1. **No simple skip-routing mistake explains the main contradiction.** All 938 initially negative boys in the target frame have an explicit `k6f26=2` lifetime-no report. The definite cross-wave contradictions appear in both tested Year 15 F19 routing groups. The audit found no positive Year 15 first-intercourse date/age variables among this negative group, and no adult `any-sex=no` coupled with `vaginal-sex=yes` in the tested male frame.
2. **Some disagreements are clearly more than an integer-age tie.** Of 49 respondents whose adult-reported first vaginal age falls before their adolescent interview age, 27 report a debut age at least two completed-year categories earlier and 22 report one earlier category. These are genuine disagreements between the records *if both responses are interpreted literally*, not independent proof of the true debut date. The severe group contributes 3.16 percentage points of the original weighted target versus 0.78 percentage points for the one-category-earlier group. The two estimates have wide intervals and unequal weights matter.
3. **The principal estimands must stay separate.** Among follow-up-responding boys initially classified as inexperienced, 75.30% reported vaginal intercourse at young-adult follow-up (from the prior harmonized analysis, n=697). In the original age-15-weighted 938-person frame, 57.99% reported vaginal intercourse if missing follow-up outcomes are set to no. Only **48.52% (95% design-based CI 41.38–55.67%)** had a retrospective debut age *strictly later* than their age at the adolescent interview. It is incorrect to call the higher values guaranteed post-interview initiation.
4. **The exact post-interview initiation proportion is not identified.** The same-age histories and undated histories cannot be ordered; the pre-interview claims cannot be adjudicated; some outcomes are missing. The 48.52% to 77.04% record-based scenario envelope assumes the adult reported ages are reliable, so is not a sharp bound on true initiation under arbitrary reporting error.
5. **The longitudinal inference is narrower but useful.** FFCWS supports substantial progression from reported adolescent inexperience to reported adult vaginal experience. It cannot establish that a majority *definitely first initiated* after Year 15, or measure current generations, or reproduce NSFG's explicitly heterosexual-vaginal-intercourse definition.

## Population, sample accounting, and survey uncertainty

The national-weight Year 15-negative male domain comprises **938** respondents. Adult vaginal status is available for **697**, of whom **514** report yes and **183** report no; **241** have an unknown status. Among 514 adult yes respondents, 503 have a valid retrospective age at first vaginal intercourse and 11 do not. The age-order categories sum to 503: 49 earlier, 52 equal, and 402 later. All six exclusive classes sum to 938.

| Classification | Raw n | Weighted share of 938 | Approx. 95% jackknife CI |
|---|---:|---:|---:|
| Retrospective age strictly after adolescent interview age | 402 | 48.52% | 41.38–55.67% |
| Reported same completed age | 52 | 4.12% | 0.93–7.32% |
| Retrospective age strictly before adolescent interview age | 49 | 3.94% | 0.83–7.06% |
| Adult vaginal yes; first age missing | 11 | 1.40% | 0.40–2.39% |
| Adult vaginal status missing | 241 | 22.99% | 15.28–30.71% |
| Adult known vaginal no | 183 | 19.02% | 13.10–24.94% |

Percentages are shares of the **full 938-person weighted domain**, not the conditional follow-up sample. Confidence intervals are script-produced 33-replicate-weight, MSE-centred normal intervals using age-15 national weights and multiplier 1; they do not account for arbitrary measurement error or all sources of nonresponse selection.

## Routing and questionnaire tests

The official FFCWS **Year 15** questionnaire asks F19 about intercourse with the *current partner*; a negative answer goes to F26, which explicitly asks whether the respondent has ever had intercourse **with anyone**. Every one of the 938 baseline-negative cases was classified from a `k6f26=2` response. There are no cases in the tested male positive-weight frame where `k6f19=1` coexists with `k6f26=2`.

The two F19 paths show the following definite earlier-debut contradictions:

| Year 15 F19 pathway | Domain n | Earlier n | Weighted earlier rate within pathway | 95% CI |
|---|---:|---:|---:|---:|
| F19 no current-partner intercourse, then F26 no lifetime intercourse | 189 | 12 | 6.14% | 0.78–11.51% |
| F19 skipped/unknown, then F26 no lifetime intercourse | 749 | 37 | 3.38% | 0.00–7.20% |

The contradiction appears in **both** pathways. Point estimates differ by 2.76 percentage points, but confidence intervals are wide and the aggregate outputs do not contain the covariance required for a proper complex-design test of this difference. **Do not claim a statistically established route effect** from these figures.

The audit also reports **zero** baseline-negative cases with valid Year 15 F20, F30 first-intercourse year or F21/F31 first-intercourse age; these were skipped as expected. Likewise, it reports **zero** adult `any sex=no`/`vaginal=yes` contradictions and zero valid adult first vaginal age later than attained adult interview age in the tested target domain. This reduces suspicion of those particular coding mistakes but does not validate the factual correctness of the interviews.

Official questionnaires:  
Year 15: https://ffcws.princeton.edu/sites/g/files/toruqf4356/files/ff_teen_q15.pdf  
Year 22: https://ffcws.princeton.edu/sites/g/files/toruqf4356/files/documents/FFCWS%20Y22%20YOUNG%20ADULT%20SURVEY_0.pdf

## How severe are the earlier retrospective ages?

The 49 definite earlier-age cases comprise **27** with debut at least two completed-year categories earlier and **22** with debut one category earlier. Their weighted full-domain contributions are **3.16%** (CI 0.10–6.22%) and **0.78%** (CI 0–1.69%), respectively. The completed-age difference is a coarse index, not an exact number of elapsed calendar years. The pattern is incompatible with explaining *all* contradictions as uncertain ordering within a single completed age. It remains compatible with retrospective errors, baseline nondisclosure, and different interpretations of 'intercourse'.

The age-specific results are also descriptive. Within those who were approximately 15 at the initial interview (n=617), 34 have a definite earlier-age conflict, with weighted rate **2.90%** (CI 1.01–4.78%). Among the 16-or-older initial-interview subgroup (n=142), the rate is **7.96%**, but with a very wide CI of **0–21.69%**. Suppressed small age-group cells should remain suppressed; a different age pattern is **not demonstrated** by these aggregates.

## Classification sensitivity and why it is not ground truth

| Record-classification assumption | Raw n | Weighted share | 95% CI |
|---|---:|---:|---:|
| Strictly later reported debut only | 402 | 48.52% | 41.38–55.67% |
| Also count all same-age cases | 454 | 52.64% | 45.26–60.03% |
| Also count adult vaginal yes with no usable debut age | 465 | 54.04% | 46.72–61.37% |
| Also count every missing adult outcome as initiating later | 706 | 77.04% | 70.49–83.58% |

These rows address **different assumptions about ambiguous/missing records**, not alternate estimates fitted to the same observed facts. The confidence intervals are each conditional on the particular scenario. Without an external check of self-report accuracy, *no scenario provides a guaranteed lower/upper bound on actual first intercourse after Year 15*.

A post hoc exercise removing the 49 definitely earlier-debut claimants from the initial negative target changes the strict-after estimate from **48.52% (938-person denominator)** to **50.51% (889-person denominator)**; its approximate 95% CI is **42.72–58.31%**. This is **not a correction**, because removing participants based on a subsequently reported outcome changes the target population, may introduce selection bias, and still does not settle which interview was wrong.

## Conclusions for the broader NSFG/YRBS critique

**Recommended wording:**

> An independent FFCWS longitudinal analysis finds that about three-quarters of follow-up respondents who denied intercourse at approximately age 15 reported vaginal intercourse by young adulthood. But retrospective debut-age reports reveal inconsistencies: 49 boys reported ages of first vaginal intercourse that predated their supposedly inexperienced adolescent interviews, while 52 supplied a first age equal to their interview age. In the full Year 15 nationally weighted sample, only 48.5% had a reported debut age unambiguously later than their adolescent interview. The substantial rise in reported sexual experience therefore supports delayed initiation as an important pattern, but the exact proportion who truly initiated between interviews is not identified. The FFCWS outcome also differs somewhat from the NSFG male heterosexual-vaginal-intercourse measure, and the findings cannot be projected to today's birth cohorts.

This evidence partially supports Alexander's historical catch-up interpretation but should **not** be presented as a definitive vindication of his extrapolations about newer cohorts. It complements, rather than replaces, the independent YRBS adolescent trend and the previously identified NSFG 2022–2023 cross-wave comparability discontinuity.

## Independent checks and limitations

`validate_aggregates.py` was run against the eight supplied aggregate outputs and passed **42 out of 42** deterministic checks. Tests cover the respondent-flow partitions, weighted identities, severity aggregation, route counts, sensitivity classifications, and CI arithmetic. They **do not** independently validate the Stata microdata, the source program's classification decisions, or the jackknife statistical assumptions. The report does not infer suppressed subgroups' counts.

The FFCWS data-use conditions mean respondent-level records should remain with the authorized researcher. This review is built entirely from privacy-screened aggregate exports.

**Research priority:** This specific forensic investigation is essentially saturated without independent validation of original responses or exact event dates. Further microdata reweighting would not resolve which wave is mistaken. The most useful next step is a consolidated scientific synthesis of the entire Alexander/GSS/NSFG/YRBS/FFCWS evidence, with a separate evidence-strength matrix and claims that each source can and cannot support; alternatively, obtain a genuinely independent cohort with repeatedly measured sexual history for external replication.


**Repository note:** This is an archived research report. References to the earlier standalone aggregate-review script or complete local CSV sets describe the historical workflow; those full intermediate bundles are not included in this release. The associated local microdata analysis programs are in `../analyses/`, the chronology aggregate used in the article is in `../figure_data/`, and the final vaginal influence results are in `../aggregate_results/`.
