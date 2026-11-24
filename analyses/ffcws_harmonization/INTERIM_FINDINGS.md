# Interim findings prior to running the new harmonized script

**Date:** November 24, 2026

The user's previously executed FFCWS longitudinal script produced the following on **separate outcome-valid denominators** among baseline males reporting no intercourse at the Year-15 interview, using Year-22 national weights:

| Outcome at Year-22 interview | Eligible observed men | Weighted probability | Approximate 95% CI, corrected jackknife multiplier |
|---|---:|---:|---:|
| Any sex (`k7e58`) | 701 | 80.0719% | about 73.0–87.1% |
| Vaginal intercourse (`k7e59`, with skip logic) | 697 | 74.26492% | about 66.5–82.0% |

The difference of about **5.81 percentage points** between these marginal estimates is merely an orientation to the measurement issue, *not a valid paired contrast*. It does not have a correct covariance-aware CI, and the four-case difference in denominator means it is not precisely the difference in experiences among identical respondents. A matched-sample contrast is produced by this package.

The prior IPW analysis yielded 80.57% for *any* sex; there was no vaginal-specific IPW or vaginal-specific worst-case missing-outcome bound in that run.

**Important correction:** An earlier exploratory script used `ck7childageinterviewm` to try to derive the young adult's 22nd birthday. That is **the age of the young adult's child**. The previous any-sex/vaginal-experience percentages did not depend on that erroneous age variable. This package instead uses `ck7yagem` and `ck6yagem` for respondent interview ages. No exact 22nd-birthday estimate has yet been independently calculated from the restricted microdata.

### What is verified now

- Question wording and routing in the official Year-15 and Year-22 questionnaires.
- Previous locally generated descriptive estimates and their separate valid sample sizes.
- Correct candidate respondent age-at-interview variables in the official Year-22 guide.
- The new local script runs successfully on generated synthetic data, including survey-weighted matched contrasts, correct skip coding, birthday eligibility and missing-outcome bounds.

### What remains unverified until the script is run locally

- Paired difference between any sex and vaginal intercourse, with proper 33-replicate CI.
- Exact vaginal-specific lower and upper bounds allowing missing adult responses.
- Interview-age distribution, percentage interviewed after the 22nd birthday, and debut before that birthday.
- Whether many retrospective debut-age reports contradict the Year-15 questionnaire timing.
- Whether age-at-15 restriction and Year-15-vs-Year-22 weighting materially alter vaginal-intercourse estimates.

Do not report any of those unexecuted measures as empirical findings.
