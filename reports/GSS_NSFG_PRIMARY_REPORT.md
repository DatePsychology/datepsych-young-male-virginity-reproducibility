# Independent replication of *Are 27% Of Young Men Really Virgins? (And Why)*

**Analytical date:** 23 November 2026  
**Status:** Executed on original, publicly released respondent-level GSS and NSFG datasets.  
**Dataset versions:** GSS 1972–2024 release 3a; NSFG male 2011–2013, 2013–2015, 2015–2017, 2017–2019, and 2022–2023.  
**Code and output:** `replicate_full.py`, `sensitivity.py`, `test_replication.py`, files in `output/`.

## Executive result

The principal published figures can be reproduced almost exactly. The 2018 GSS figure of **24.93%** for heterosexual men aged 18–30 is obtained with original `WTSS`, treating nonmissing `NUMWOMEN > 0` as not zero. The 2021 article figure of **16.64%** is obtained with `WTSSPS`. The 2018 **50.52%** subgroup corresponds to ages **18–19** (only 14 observed men, six with zero female partners since 18); **1.90%** corresponds to ages **26–30** (one positive event). In the 2017–2019 NSFG, the heterosexual male percentages are **24.20%** (18–24), **15.27%** (18–29), and **3.95%** (25–30), agreeing with the original charts.

The survey-design-adjusted comparison **does not establish** a decline in `NUMWOMEN == 0` between 2018 and 2021: consistent `WTSSNRPS` estimates are **22.51%** (95% CI 14.27–33.64, n=124) and **16.64%** (8.32–30.51, n=87), change **−5.87 percentage points** (95% CI −20.44 to +8.70; exploratory p=.429). The 2021 design/mode break is **not** repaired by confidence intervals.

For heterosexual men aged 18–29, NSFG **no lifetime heterosexual vaginal intercourse** is **15.27%** (12.22–18.91, n=1,711) in 2017–2019, compared with **27.55%** (24.01–31.39, n=1,168) in 2022–2023. The nominal wave difference is **+12.28 points** (95% CI +7.36 to +17.21; p ≈ .000003), assuming independent releases. However, NSFG changed to a multimode web/in-person survey in 2022. The *2022–2023* rate is **20.88%** (16.00–26.76; n=353) among heterosexual 18–29 respondents interviewed **face-to-face**, and **30.61%** (26.53–35.02; n=815) in **web** respondents. The mode-only breakdowns are diagnostic, **not** separately representative population estimates, because the released final weights calibrate the whole sample rather than each interviewing-mode subsample. Among men aged 25–30 identifying as heterosexual, the corresponding survey rates are **3.95%** (2017–2019), **15.51%** (2022–2023 overall), **7.93%** (face-to-face), **18.79%** (web). The mode difference and redesign prevent an automatic behavioral-change inference.

The age-standardized (2017–2019 heterosexual 18–29 reference composition) NSFG estimates are 15.27% and 27.10% for 2017–2019 and 2022–2023, respectively. Changing age composition therefore does not explain the all-mode point-estimate gap. This check does **not** resolve mode/selection changes.

For the GSS **zero sex partners in the previous 12 months** among all men aged 18–29, weighted percentages are **25.58%** (17.00–36.60) in 2018, **19.18%** (11.00–31.28) in 2021, **11.36%** (5.60–21.66) in 2022, and **24.91%** (15.44–37.61) in 2024. Uncertainty is considerable; 2018 vs 2024 contrast −0.67 points (95% CI −15.45 to 14.11; p=.93). `NUMWOMEN` is **unavailable in GSS 2024**, so its 2018-to-2024 trend cannot be computed directly.

## Prespecified three outcomes

1. `GSS: PARTNERS == 0`: no sex partners reported for preceding 12 months. `PARTNERS` harmonized categorical code 0=none; 9=one-or-more unspecified. This is *not* lifetime virginity.
2. `GSS: NUMWOMEN == 0`: zero **female** sexual partners since 18, not zero lifetime sexual experience. Valid positive counts 1–989 **plus qualitative positive codes 991 (one or more), 994 (several), 995 (many/lots)**. Ambiguous or refused 990, 992, 993, 996, 997 are excluded. The article's original comparisons simply count nonmissing nonzero NUMWOMEN as a negative outcome, a negligible difference to the currently observed 2018–2021 subsample when their original weights are used.
3. `NSFG: HADSEX == 2`: never vaginal intercourse with a female. It does *not* exclude oral sex, anal sex, or sexual experiences with men. For heterosexual-only subsets: NSFG 2011–2015 `ORIENT==1`, 2015–2019 `ORIENT_A==1` or `ORIENT_B==2` (random questionnaire split), 2022–2023 `ORIENT==2`.

## Estimation

- Weighted proportions with `WTSSNRPS` in GSS (primary; used for all 2008–2024 waves) and `WGTxxxx_yyyy` in NSFG; original `WTSS`/`WTSSPS` replicated as a benchmark.
- Taylor with-replacement stratified **PSU** variances on the full wave's design. GSS `VSTRAT`, `VPSU`. NSFG through 2019 `SEST`, `SECU`; 2022–2023 `VEST`, `VECL`. Domain estimates preserve PSUs with no eligible subgroup members (zero linearization contribution).
- 95% confidence intervals: survey-design t critical values (all wave design PSU count minus strata) with logit-transformed interval bounds. Wave contrasts: differences on percentage-point scale with Satterthwaite t reference, **assuming waves independent**, with no adjustment for cross-wave design dependence, multiple exploratory contrasts or questionnaire/survey-mode changes. In particular, independent contrasts spanning NSFG 2022–2023 are not causal/time-series estimates.
- Age groups are reported explicitly; overlapping groups are never aggregated. Counts are unweighted, proportions weighted. Missing/ambiguous survey responses omitted from relevant outcome denominator.

## Main limitations and cautions

- GSS respondent counts for young male subsamples are small. The 2018 original 18–19 n=14, 2021 18–19 n=5; estimates for such groups are unstable.
- The article compares different GSS weights across 2018 and 2021. The mode and sample selection methods also changed in 2021.
- Poststratified survey sampling CIs do *not* account for systematic self-report error, nonresponse not covered by weights, or mode-driven reporting differences.
- The 2022–2023 NSFG mode-restricted analysis is exploratory and not a design-unbiased estimate of the national population's face-to-face counterfactual. Mode was not randomized. Both the composition of respondents and reporting mode may differ.
- NSFG 2011–2019 releases are separate repeated cross sections. Their design-stage clustering may be related across waves; the difference test uses independent-wave approximations. A full design-dependent trend test would need additional PSU/covariance documentation or appropriate combined-release design files. Treat the individual-wave design CIs as the primary reliable inferential results.
- There are **three distinct constructs**; cross-survey discrepancies cannot be resolved by directly equating them.
- Multiple subgroups and wave contrasts are exploratory. Marginal 0.04–0.05 p-values are not confirmatory.

## Key official documentation (accessed 2026-11-23)

- GSS 1972–2024 Release 3a: https://gss.norc.org/get-the-data/stata.html
- GSS FAQ on WTSSPS vs WTSSNRPS: https://gss.norc.org/faq.html
- CDC NSFG 2022–2023 documentation: https://www.cdc.gov/nchs/nsfg/documentation/2022-2023.html
- CDC male NSFG 2022–2023 codebook: https://www.cdc.gov/nchs/data/nsfg/codebooks/2022-2023-NSFG-MalePUFCodebook.pdf
- CDC questions/weighting: https://www.cdc.gov/nchs/data/nsfg/guidefaqs/NSFG-2022-2023-FAQ.pdf
- NORC 2021 design information: https://gss.norc.org/get-documentation.html
- GSS NUMWOMEN value descriptions, including 991/994/995: https://kjhealy.github.io/gssrdoc/reference/numwomen.html

The full respondent microdata are not redistributed. Place source files in `input/` as described in `README.md` to rerun the analysis. The archive includes scripts, non-disclosive aggregated results and figures.
