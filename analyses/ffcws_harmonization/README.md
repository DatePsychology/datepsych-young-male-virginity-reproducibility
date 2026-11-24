# FFCWS: harmonized vaginal-intercourse and birthday-timing investigation

**Study:** FFCWS / ICPSR 31622, DS0001 all-years public-use microdata (the local file usually called `31622-0001-Data.dta`).  
**Version:** 2026-11-24.  
**Privacy:** Run the script on your own computer. ICPSR restricts transfer of respondent-level data to AI systems. The script never exports individual records, ID numbers, individual predictions, or data values. Only aggregate CSV, JSON and an aggregate Markdown summary are produced. Output cells with 1–9 members or 1–9 positive/negative outcomes are suppressed when producing outcome estimates.

## Why the analysis is needed

The previous aggregate FFCWS analysis found that, among boys who reported no intercourse at approximately age 15, **80.0719%** (n=701, Year-22 national weights) reported *any sex* by the Year-22 interview, whereas **74.26492%** (n=697, same nominal weighting) reported *vaginal intercourse*. These estimates are not a valid paired comparison, because they use slightly different outcome-validity denominators. Neither figure establishes experience by the **22nd birthday**: the name of the survey wave is not a precise age-at-interview variable.

This new analysis:

1. Uses the **identical respondents** for the any-sex versus vaginal-intercourse contrast and estimates its 33-replicate jackknife SE directly on the respondent-level difference.
2. Repeats the principal Year-15-weighted, Year-22-weighted and baseline inverse-response-probability-weighted transition estimates.
3. Computes the vaginal-intercourse **sharp missing-outcome bounds** in the Year-15 weighted frame, as before for the any-sex outcome.
4. Uses the **correct respondent age** at interview: `ck6yagem` for the Year-15 interview and `ck7yagem` for Year-22, in months. **Do NOT use `ck7childageinterviewm`: this is the age of the *respondent's child* (generation 3), which an earlier script mistakenly referenced.**
5. Using `k7e60` (integer age at first vaginal intercourse), computes birthday-restricted estimates among respondents who have **already attained** the relevant birthday at interview. Those who have not yet attained it are censored and **not treated as virgins at that age**.
6. Reports prevalence of first vaginal intercourse in five age categories, among respondents reporting vaginal intercourse and providing a valid debut age.
7. Audits missing ages, questionnaire routing, and retrospective chronology; compares a sensitivity subgroup who were aged 15 through before 16 when completing the adolescent interview.

### Critical definition limitations

- The Year-15 interview asks whether the teen had **sexual intercourse** with a current romantic partner (`k6f19`) or anyone (`k6f26`), but **does not explicitly specify vaginal intercourse**. Routing must be respected: some respondents reporting yes to `k6f19` skip `k6f26`.
- The Year-22 interview separately asks any sex (`k7e58`), vaginal intercourse (`k7e59`), and integer age at first vaginal sex (`k7e60`). A respondent answering **no** to `k7e58` is routed past `k7e59`: the skip implies **no vaginal intercourse**. Other negative codes, refusals, and missing values are **not** recoded as no.
- The FFCWS `k7e59` question does **not** specify the sex/gender of the vaginal-intercourse partner or the respondent's sexual orientation. It is *closer to*, but not identical with, NSFG male lifetime **heterosexual vaginal intercourse**. Do not label these estimates “heterosexual virginity rates.”
- Year-22 is a wave name; people were interviewed at varying ages. `ck7yagey` is **rounded to the nearest year** in the guide; use `ck7yagem` to establish exact attained birthdays.
- Integer age at first intercourse is retrospective and cannot establish the exact month of initiation. When the reported debut age equals the completed age at the Year-15 interview, it could have happened before **or after** that interview. This is reported as ambiguous, **not** as a contradiction.
- Birthdays are studied only among people interviewed after the age threshold. This *attained-age-conditioned subset* may be selected; it is not a formal survival estimate correcting for right-censoring. The script does **not** claim an age-standardized hazard or a national cohort effect.
- FFCWS has **no dedicated Year-15-to-Year-22 national longitudinal weight**. These are two wave-specific weighting approaches plus a transparent response-model sensitivity.

## Windows PowerShell — run locally

The user previously installed **Python 3.12** for this research. Keep using it. Extract the ZIP, open PowerShell in the extracted folder, and type:

```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 test_harmonize_synthetic.py
```

The expected final line is:

`Synthetic harmonization tests passed: routing, paired gaps, birthday eligibility, full aggregate output.`

Then run, **replacing the example path** with the location of the authorized ICPSR dataset:

```powershell
py -3.12 harmonize_ffcws.py --allwaves "C:\Research\ICPSR_31622\DS0001\31622-0001-Data.dta" --out "C:\Users\Me\Downloads\FFCWS-Harmonized-Results" --strict
```

`--strict` requires the original analysis sample size and approximately reproduces the two previously shared Year-22 estimates (80.0719% and 74.2649%). If it fails, preserve and report the full error. Do not manually alter the data or silently disable the check.

The test takes seconds; the complete 33-replicate response-model analysis will take longer. It may warn if some retrospective reported ages are chronologically inconsistent; those are *audited*, not silently deleted.

## Files to share

Zip the **results folder** and attach it in the chat. It will contain only aggregates:

| Output file | Contents |
|---|---|
| `SUMMARY.md` | Topline matched results and bounds |
| `harmonized_outcomes.csv` | Any sex, vaginal intercourse, matched comparisons; three weighting approaches |
| `matched_outcome_gap.csv` | Same-person difference and its covariance-aware jackknife CI |
| `outcome_missingness_bounds.csv` | Sharp 0/1 assignments for missing any-sex and vaginal outcomes |
| `birthday_milestones.csv` | Fixed birthdays 18, 20, 21, 22, 23, restricted to those old enough |
| `age_at_first_vaginal.csv` | Retrospective age-at-first proportions among initiators |
| `interview_age_profile.csv` | Respondent ages at adolescent and young-adult interviews |
| `age15_restricted_outcomes.csv` | Sensitivity subset actually interviewed at age 15 |
| `routing_and_quality_audit.csv` | Questionnaire skips, chronology, and missing data |
| `analysis_metadata.json` | Coding rules, denominator diagnostics and version checks |

Do **not** upload the original `31622-0001-Data.dta` file, row-level extracts, temporary individual predictions, or respondent identifiers.

## Interpreting the results

Use the **same-denominator** `sex_without_vaginal_matched` estimate to measure how much the broader any-sex definition changes the conclusion. The `vaginal_intercourse` estimate is the better NSFG approximation, but still not definition-identical. Do not subtract the historical 80.1% and 74.3% as though the two analyses used exactly the same cases.

From `outcome_missingness_bounds.csv`, the lower bound for `vaginal_intercourse` is especially important: does the **vaginal-specific** majority-initiation conclusion remain true even when every eligible respondent with missing follow-up vaginal status is assumed to have **not initiated**? The reported point bound is conditional on the Year-15-weighted study frame and does **not** include sampling uncertainty or survey nonresponse prior to Year 15.

For `birthday_milestones.csv`, never interpret a Year-22 interview as automatically occurring after the 22nd birthday. Also note that excluding respondents interviewed before an age threshold is a **selected subsample**, not a full Kaplan–Meier estimate. Age-at-first sex is recorded in completed integer years, so respondents with the first-vaginal-intercourse age of 22 did **not** experience vaginal intercourse *before* their 22nd birthday.

## Source documents

- [Year-15 original teen questionnaire (F19, F26)](https://ffcws.princeton.edu/document/901)
- [Year-22 young-adult questionnaire (E58–E60 and skip routing)](https://ffcws.princeton.edu/document/1981)
- [Year-22 public guide (constructed respondent ages `ck7yagem` / `ck7yagey`)](https://ffcws.princeton.edu/sites/g/files/toruqf4356/files/documents/CLEAN_year_22_guide_updated%20by%2011.04.2026.pdf)
- [FFCWS public documentation](https://ffcws.princeton.edu/data-and-documentation/public-data-documentation)
- [Study weights documentation](https://ffcws.princeton.edu/sites/g/files/toruqf4356/files/documents/using_the_fragile_families_weights_waves_1_6_06082026.pdf)
