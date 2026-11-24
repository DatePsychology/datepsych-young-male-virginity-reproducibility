# Adult sexual initiation and cross-wave retrospective comparability: NSFG male audit

**Analysis date:** 23 November 2026. Original CDC public-use NSFG male respondent datasets: 2011–2013, 2013–2015, 2015–2017, 2017–2019, 2022–2023. Code and data-dependent tables included with this report. Exploratory investigation, not a preregistered confirmatory analysis.

## Executive synthesis

The historical NSFG waves consistently show substantial vaginal-intercourse initiation in the early twenties. Among 25–29-year-old men surveyed in 2017–2019, 19.67% had not experienced heterosexual vaginal intercourse before their 21st birthday, compared with 11.25% before their 25th. Of those still inexperienced on the 21st birthday, an estimated 42.82% initiated before the 25th (survey-design-adjusted 95% interval 32.75–52.88%). Across four historical waves this conditional proportion ranged from 42.8% to 55.7%.

The 2022–2023 wave instead finds 37.54% with no intercourse before age 21 and 24.04% before age 25 in the sampled 25–29 age group. An apparent large increase in delayed initiation is therefore present. However, a *fixed-historical-milestone diagnostic* demonstrates serious inconsistency across releases: for an approximately identical birth cohort whose 21st birthday had already passed, the reported prevalence of never having had vaginal intercourse before age 21 **changes markedly** from 2017–2019 to 2022–2023, despite being approximately stable over earlier waves.

**Among men born approximately 1985–1989:** reported no intercourse before age 21 = 18.96% in 2017–2019 (n=864) and 35.50% in 2022–2023 (n=753). Difference +16.54 percentage points; independent-wave design-based 95% confidence interval +10.82 to +22.26. **Born approximately 1990–1994:** 19.63% (n=765) versus 37.59% (n=714); +17.96 points (CI +9.44 to +26.48). Before the 2022 redesign, the 1985–1989 cohort's age-21 retrospective percentages were 17.73%, 18.73%, 20.51%, and 18.96% across the four older waves. The 1990–1994 cohort also had much lower reported percentages before 2022–2023, though earlier waves sometimes observe only an age-eligible subset of that cohort.

Because whether an individual had sex before the 21st birthday was settled long before either wave, changes in 2019–2023 sexual behavior cannot explain the same-cohort retrospective difference. Sampling and population composition, nonresponse, mode, questionnaire and recode changes, or retrospective recall must be considered. This is powerful evidence against interpreting the 2022–2023 wave difference as a direct estimate of true behavioral change. It does NOT prove that no behavioral change occurred for more recent cohorts, nor isolate a causal mechanism of measurement error.

## Outcome and inference

Primary population is **all men**, without conditioning on their current sexual orientation, to avoid a potentially post-initiation restriction. A secondary heterosexual-only analysis gives similar qualitative findings. Define `S(T)=1` for (a) respondent never had vaginal intercourse with a female as of interview, or (b) his first such intercourse was at a completed age >=T; include respondents current age >=T. Thus `S(21)=1` means *no intercourse before the 21st birthday*; this threshold is fixed throughout adulthood. It does NOT mean zero sexual activity with men or zero oral/anal sex.

The NSFG `VRY1STAG` public-use recode is bottom-coded at 10 for 2017–2019 and 2022–2023. Before that, more detailed ages below 10 appear; this does not affect cutoffs at 18/21/25. An implausible 2011–2013 record with reported first intercourse age exceeding age at interview was excluded from threshold analyses; no further date inconsistencies were found in the five waves.

Weights and design: historical `WGTyear_year`, `SEST`, `SECU`; newer `WGT2022_2023`, `VEST`, `VECL`; full-wave PSU/stratum Taylor-linearized domain variance (survey t critical for CIs). Independent-wave Satterthwaite intervals for contrasts, with approximate survey independence; repeated sampling frames, retrospective recall and design differences are not accounted for in those intervals. A separate stratified rescaled-PSU bootstrap with 1,600 draws found fixed-cohort difference CIs of +10.50 to +22.12 (1985–89) and +10.08 to +26.01 points (1990–94), closely matching linearized intervals. Inferential p-values are exploratory; large and robust point gaps matter more than formal significance alone.

## Historical progression among men aged 25–29

| Wave | Never before 18th birthday | Never before 21st birthday | Never before 25th birthday | Never at interview |
|---|---:|---:|---:|---:|
| 2011–2013 | 39.08% | 19.77% | 9.27% | 6.65% |
| 2013–2015 | 41.33% | 18.15% | 8.04% | 3.99% |
| 2015–2017 | 42.82% | 19.27% | 10.57% | 7.71% |
| 2017–2019 | 41.37% | 19.67% | 11.25% | 6.93% |
| 2022–2023 | 60.20% | 37.54% | 24.04% | 19.33% |

Estimated initiation during ages 21–24, conditional on no intercourse before age 21:
2011–13 53.12% (CI 42.79–63.45), 2013–15 55.69% (43.37–68.02), 2015–17 45.16% (34.15–56.16), 2017–19 42.82% (32.75–52.88), 2022–23 35.96% (27.65–44.27). These are retrospective conditional fractions, not prospective hazards; there is no causal explanation from this alone. The difference in the 2017–19 and 2022–23 conditional fraction is not clearly distinguishable from sampling variability and is additionally confounded by redesign.

## Fixed milestone comparison within approximately identical cohorts

| Approximate birth cohort | Wave | No intercourse before 21st birthday |
|---|---|---:|
| 1985–1989 | 2011–2013 | 17.73% |
| 1985–1989 | 2013–2015 | 18.73% |
| 1985–1989 | 2015–2017 | 20.51% |
| 1985–1989 | 2017–2019 | 18.96% |
| 1985–1989 | 2022–2023 | 35.50% |
| 1990–1994 | 2017–2019 | 19.63% |
| 1990–1994 | 2022–2023 | 37.59% |

For 1985–1989, the earlier-wave 2011–2013 to 2017–2019 change was +1.24 points (95% interval −4.55 to +7.02; p=.67), versus +16.54 points on crossing the 2022–2023 redesign. Equivalent discrepancies for the same 1985–1989 cohort appear for before 18 (difference +13.45 points) and before 25 (difference +10.35 points). Restricting birth-year bands to 1986–88 gives a +23.15-point difference at the age-21 threshold, and to 1991–93 gives +18.58 points. They are not an artifact of year-of-birth ±1 calendar-year uncertainty. Detailed results in `output/same_cohort_fixed_milestone_contrasts.csv` and `output/birthyear_bin_sensitivity.csv`.

### Interview mode is informative, not an identified cause

In 2022–2023 for the 1985–1989 cohort, weighted percent no vaginal intercourse before age 21: face-to-face 19.07% (n=169), web 40.91% (n=584). The FTF estimate happens to be near the 2017–2019 all-mode 18.96%. For the 1990–1994 cohort, the corresponding FTF/web estimates are 30.79% and 40.47%, so there is no uniform correction. 2022–2023 was web-first, with FTF offered to web nonrespondents: these are nonrandom respondent groups, and each subgroup is not independently reweighted to the national population. The strong mode correlation does not identify the causal portion due to reporting versus participation differences.

### Recode comparability issue verified from CDC documentation

The CDC 2017–2019 male recode specifications (pp. 23–24) describe `VRY1STAG` drawn sometimes from a directly asked first-sex age and sometimes from an intercourse date, depending on first-partner routing. The CDC 2022–2023 male recode specifications (p. 18) define `VRY1STAG` using a computed completed age from imputed calendar month of first intercourse minus calendar month of birth. **The recode construction is not identical across releases.** This alone cannot be assigned the observed difference, but it is a substantive comparability limitation beyond interview mode. Official documents:

- https://www.cdc.gov/nchs/data/nsfg/NSFG-2017-2019-UG-App3c-MaleRecodeSpecs-508.pdf
- https://www.cdc.gov/nchs/data/nsfg/recodespecs/2022-2023-NSFG-Male-RecodeSpecs.pdf
- https://www.cdc.gov/nchs/data/nsfg/guidefaqs/NSFG-2022-2023-UsersGuide-revJuly2025.pdf

## What the investigation does and does not answer

1. **Supports postponement:** A substantial portion of older historical respondents still inexperienced at 21 had initiated by 25. Late first intercourse is therefore not generally synonymous with permanent lifetime virginity, and the article's age-gradient observation is credible for historical groups.
2. **Does not establish recent persistence:** The youngest cohorts that show less teen sex have not all reached 25 under a stable NSFG design. A historical 25-year-old transition probability is not a guaranteed prognosis for newer cohorts.
3. **Strongly cautions against a literal interpretation of 2022–2023:** The same already-completed milestone appears very different for approximately identical cohorts in older and newer surveys. Extrapolating the reported 2022–23 25–29 inexperience levels to actual generational prevalence without qualification is unsound.
4. **Cannot prove mode bias alone:** Cohorts are independently resampled; net migration, mortality, nonresponse, respondent composition, recall, survey-mode or instrument changes can alter measured percentages. Birthyear is approximate. The numbers do not identify a unique mechanism or a corrected prevalence.
5. **Not all sex:** NSFG measures heterosexual vaginal intercourse, not every possible sexual experience. Childhood experiences, voluntary versus coerced initiation, and sexual orientation are not resolved by this single outcome.

## Highest-value follow-up

A formal bridge design, with randomly assigned survey modes and equivalent interview questions for the same population, would be the definitive way to identify mode/measurement effects, but these data are unavailable. More feasible next steps: (i) within-cohort 2022–23 reweighting for observable characteristics plus careful examination of sampling/response changes (without causal interpretation); (ii) external longitudinal adolescent-to-adult cohort evidence, such as Add Health or NLSY97, if appropriate sexual-initiation questions and access are available, to distinguish recent postponement from persistence. Given the direct cohort falsification result, further uncritical adjustment of NSFG 2022–23 cannot settle that issue.
