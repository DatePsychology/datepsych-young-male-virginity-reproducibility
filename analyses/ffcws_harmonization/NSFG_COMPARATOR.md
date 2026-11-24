# Historical NSFG comparator — for context, **not** a pooled estimate

Source: the preceding independent NSFG 2011–2023 age-at-first-intercourse audit, reproducibility file `nsfg_adult_transition/threshold_prevalence_by_wave.csv`, already completed in this project using CDC public-use male respondent microdata and complex survey design variables.

For **all men aged 25–29** at interview (so everyone had already passed their 22nd birthday), the proportion who reported **not having had heterosexual vaginal intercourse before the 22nd birthday** was:

| NSFG interview wave | Inexperienced before 22nd birthday | Experienced before 22nd birthday (complement) |
|---|---:|---:|
| 2011–2013 | 17.0% | 83.0% |
| 2013–2015 | 14.8% | 85.2% |
| 2015–2017 | 15.2% | 84.8% |
| 2017–2019 | 16.1% | 83.9% |
| 2022–2023 | 33.3% | 66.7% |

**Not directly comparable to FFCWS:**

1. These are population-wide male NSFG samples; the FFCWS analysis instead conditions on boys **reporting no intercourse at their Year-15 interview** and positive Year-15 national weights, drawn from large-city births 1998–2000.
2. The age-22 NSFG threshold here refers to **experience before the 22nd birthday**, while the previously reported FFCWS 74.3% refers to experience **by the Year-22 interview**, at varying ages. The new local script will estimate fixed birthday thresholds in FFCWS only among those who have attained each birthday.
3. The NSFG outcome explicitly refers to vaginal intercourse with females, whereas FFCWS's vaginal-intercourse question does not explicitly specify the sex/gender of the partner.
4. The 2022–2023 NSFG retrospective estimates have a demonstrated serious cross-wave comparability problem after redesign and should **not** be treated as precise real cohort-change measures.
5. Confidence intervals, weighting, and samples are distinct. Differences in percentages between studies **do not** measure causal or even directly comparable population trends.

Once the restricted FFCWS local aggregates are executed, a more carefully defined comparison may be made, still observational and non-equivalent.
