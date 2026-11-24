# Source and reproducibility audit

## Primary sources and estimands

| Source | Data acquisition | Outcome and analytical limits |
|---|---|---|
| Date Psychology, 2023 | https://datepsychology.com/are-27-of-young-men-really-virgins-and-why/ | Original claims and graphs; original weighting choices reconstructed. |
| GSS | https://gss.norc.org/get-the-data/stata.html | NUMWOMEN = 0 is no female partners since age 18, not lifetime virginity. PARTNERS = 0 measures past-year sexlessness. Consistent comparison uses WTSSNRPS; 2021 mode changed. |
| NSFG | https://www.cdc.gov/nchs/nsfg/documentation/2017-2019.html and https://www.cdc.gov/nchs/nsfg/documentation/2022-2023.html | Male HADSEX = 2 means no lifetime vaginal intercourse with a female; VRY1STAG measures reported completed age at debut. Restrict milestone estimands to those reaching the relevant birthday. Birth cohorts are approximate; independently sampled waves do not track individuals. |
| National YRBS | https://www.cdc.gov/yrbs/data/national-yrbs-datasets-documentation.html | Ever had sexual intercourse among sampled school-enrolled respondents. Year-specific variables and survey design described in `analyses/yrbs_nsfg/README.md`. |
| FFCWS | https://www.icpsr.umich.edu/web/DSDR/studies/31622 and https://ffcws.princeton.edu/documentation | Year-15 lifetime intercourse report and Year-22 separate any-sex and vaginal-intercourse outcomes. Initial national-weight frame represents large-city births, not all US boys. Local authorized processing only. |

Questionnaire and design references: [FFCWS Year 15 questionnaire](https://ffcws.princeton.edu/sites/g/files/toruqf4356/files/ff_teen_q15.pdf), [Year 22 questionnaire](https://ffcws.princeton.edu/sites/g/files/toruqf4356/files/documents/FFCWS%20Y22%20YOUNG%20ADULT%20SURVEY_0.pdf), [NSFG 2022–2023 guide](https://www.cdc.gov/nchs/data/nsfg/guidefaqs/NSFG-2022-2023-UsersGuide-revJuly2025.pdf), [GSS 2021 methods](https://gss.norc.org/content/dam/gss/get-documentation/pdf/other/2021%20XSEC%20Methodological%20Primer.pdf). See individual reports for additional sources and formulas.

## Figure provenance

The filenames are stable identifiers rather than their order of appearance in the article. `article_figures/` contains exact original PNGs; `reproduced_figures/` contains regenerated, visually comparable versions.

| File | Article label | Inputs and interpretation |
|---|---|---|
| 01_gss_uncertainty.png | Figure 1 | Archived GSS estimates and contrast from `analyses/gss_nsfg/output/`; values transcribed in figure script. Survey-design uncertainty. |
| 02_yrbs_boys_trend.png | Figure 2 | `figure_data/yrbs_prevalence_all.csv`, `yrbs_missingness_sensitivity.csv`; age-standardized 2019 and 2021 markers from `analyses/yrbs_nsfg/output/yrbs_standardized.csv`. |
| 03_nsfg_discontinuity.png | Figure 3 | `figure_data/gss_nsfg_prevalence_all.csv`; mode-specific bootstrap point and interval values transcribed in script from historical analysis. Nonrandom modes, different uncertainty methods. |
| 04_nsfg_fixed_cohort.png | Figure 4 | `figure_data/nsfg_threshold_prevalence.csv`; age-eligible milestone reports, 2022–2023 points disconnected. |
| 05_ffcws_flow.png | Figure 5 | Counts in `figure_data/chronology_components.csv` and archived forensic report. Counts are not survey-weighted. |
| 06_ffcws_histories.png | Figure 6 | Six mutually exclusive chronology classes in `figure_data/chronology_components.csv` (the two additional adult-known-yes and known-status rows are overlapping summaries, not additional exclusive categories). |
| 07_survey_measures.png | Figure 1A | `figure_data/survey_measures.csv`; qualitative comparison drawn from the article, not a statistical estimate. |
| 08_yrbs_sensitivity.png | Figure 2A | `analyses/yrbs_nsfg/output/yrbs_missingness_age_grade_MNAR.csv` and `figure_data/yrbs_missingness_sensitivity.csv`; model scenarios and worst-case ranges, not confidence intervals. |
| 09_nsfg_thresholds.png | Figure 4A | `analyses/nsfg_fixed_cohort/output/same_cohort_fixed_milestone_contrasts.csv`; all men born approximately 1985–89, 2017–2019 versus 2022–2023. |

## Statistical and computational scope

GSS, historical NSFG and YRBS scripts use survey-weighted domain proportions, stratified PSU Taylor linearization and design-based confidence intervals as described in module READMEs. Wave comparisons use independent-wave variance approximations. The mode audit uses a 400-replicate stratified rescaled bootstrap, with a weighted historical reference distribution and models including age (linear and quadratic), race/ethnicity and harmonized education. Raw face-to-face difference reported in article: +5.61 pp, exploratory interval −0.25 to +11.87; standardized contrast +7.48 pp, +0.54 to +14.10. The archived mode contrast CSV does not include the raw contrast; it is now explicitly computed by the recovered script when rerun. These diagnostics do not identify causal mode effects or eliminate nonresponse bias.

FFCWS Year-15 weighting and separate Year-22 weighting do not constitute dedicated cross-wave longitudinal weighting. The local influence audit refits the response-probability model and recalculates adaptive capping thresholds for 33 jackknife replicates; paired difference intervals are exploratory. Capping and deletion are influence diagnostics, not corrections. Chronology inconsistencies and missing follow-up status preclude identifying an exact post-interview initiation proportion. The final local run passed 12 historical checks; `aggregate_results/aggregate_review_checks.json` documents 72 previously completed independent checks of rounded aggregates. The new root tests are separate selected checks, not a replication of all 72 tests or of respondent-level analyses.

## Archive limitations

The historical FFCWS harmonization and forensic reports refer to full intermediate aggregate bundles and standalone validation code not present in the supplied final archive. We retain the reports, local scripts, article chronology aggregates and final vaginal influence outputs, rather than inventing missing files. Earlier reports may contain preliminary results later refined in the article; use the final audit report and chronology categories for the latest interpretation. The original raw survey inputs are intentionally absent. No new survey microdata analyses were conducted during this GitHub packaging step. Historical module output directories may be overwritten if their scripts are rerun; preserve copies if comparing versions. The YRBS missing-data model is restricted to age and grade and does not account for nonparticipating schools or students. The root chart script includes a few explicitly transcribed historical values; not every plotted quantity is recomputed from microdata by the root script.
