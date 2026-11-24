# Forensic audit of incompatible FFCWS Year 15 and Year 22 sexual histories

**Evidence reviewed:** All nine aggregate outputs from the local FFCWS harmonization, the original `harmonize_ffcws.py` source, and the official Year 15 and Year 22 questionnaires. Restricted respondent-level ICPSR microdata remain on the researcher's computer; **the new forensic program has been tested on synthetic data, not run on the restricted file**.

## 1. Principal empirical finding, from the previous local-run aggregates

Among 938 nationally weighted boys classified as having reported **no intercourse** at the adolescent interview, 697 had a usable young-adult vaginal-intercourse outcome. The weighted observed-case follow-up vaginal-intercourse proportion was 75.30% (95% design-based CI 67.89–82.71%).

Of the 514 initially negative males who reported vaginal intercourse at the adult interview, 503 also reported a valid completed age at first vaginal intercourse. Comparing those integers with completed age at the adolescent interview yields:

| Record-based chronology | Unweighted n | Weighted proportion of entire 938-person Year 15 target |
|---|---:|---:|
| Adult-recalled first age **strictly earlier** than Year 15 age | 49 | **3.9442%** |
| First age **equal** to completed Year 15 age | 52 | **4.1226%** |
| First age **strictly later** than Year 15 age | 402 | **48.5206%** |
| Adult reports vaginal intercourse; first-age report missing | 11 | **1.3984%** |
| Adult vaginal-intercourse status missing | 241 | **22.9940%** |
| Adult explicitly reports no vaginal intercourse (including valid skip) | 183 | **19.0202%** |

The six weighted categories sum to 100%; the six unweighted counts sum to 938. Weighted values are from `routing_and_quality_audit.csv` and `outcome_missingness_bounds.csv` and are conditional on original interview responses. *They are not estimates of independent verification of the true sexual histories.*

## 2. A correction to our prior conservative calculation

A previous report proposed 49.92% as a conservative confirmed-post-teen lower proportion after excluding the 49 pre-interview and 52 same-age cases from the all-missing-no adult vaginal estimate. **That was too generous for a strict confirmed-post-interview claim.** It still counted the eleven vaginal-positive respondents without valid first-age reports, whose ordering relative to Year 15 is unknown.

The strictly age-ordered *observed* post-interview proportion is **48.52%** in the original age-15-weighted frame. The earlier **49.92%** was a sensitivity scenario, not a guaranteed proven chronology proportion.

Under the **additional assumption that the adult-reported integer age of first vaginal intercourse is accurate**, the record-based classification envelope for initiation after the adolescent interview is:

- **Lower identified-from-records share: 48.52%**, classifying the 52 same-age, 11 undated adult-positive, and 241 adult-outcome-missing cases as not having confirmed post-interview intercourse.
- **Upper possible share: 77.04%**, classifying all those cases as having initiated after the adolescent interview while excluding the 49 with explicitly earlier recalled debut ages and all 183 adult-known negatives.

These are **scenario endpoints, not empirically justified corrections and not sharp bounds on true initiation under arbitrary recall/reporting errors**. For reference, the wider outcome measure “vaginal intercourse by adult interview” has missing-outcome point bounds 57.99%–80.98%, and the 95% survey CI for its pessimistic bound includes 50% (49.74%–66.23%).

## 3. The original questionnaire routing is not the suspected problem—unless data reveal violations

In the official **Year 15** questionnaire, F19 asks about intercourse with the *current partner*. Those answering F19 no/refuse/don't know go to F26, which asks about intercourse **with anyone**. A teen whose F19 answer was yes bypasses F26 to the first-sex questions. Consequently, a baseline `no intercourse` classification based on `k6f26=2` and `k6f19!=1` is a valid **lifetime no** report, rather than a mistaken inference from no sex with a current partner.

The Year 15 **F20/F20A** date refers to first intercourse *with that current partner* and **F30/F30A** refers to a first sexual encounter in the applicable sex-positive questionnaire routing. Neither date is normally present for boys who answered lifetime **no** at F26. They therefore cannot, in general, supply a missing first-intercourse date to reconcile the 49 contradictory and 52 ambiguous records.

The local forensic program nevertheless checks for positive event dates/ages in cases where the questionnaire should have skipped them. It also cross-tabulates contradictions against the partner-route type and the age at Year 15 interview. These checks can reveal routing/data anomalies if any exist, but they cannot retroactively authenticate a recalled sexual history.

The **Year 22** questionnaire E58 asks any sex; E59 asks ever vaginal intercourse; E60 asks first vaginal intercourse **age**, not event month and year. A `no` answer at E58 intentionally skips E59; treating that as no vaginal intercourse is justified. The integer E60 age makes same-completed-age timing intrinsically ambiguous.

## 4. What the new local audit will discriminate

1. **Route-specific conflicts:** are definite earlier-age conflicts concentrated among boys who answered current-partner F19=no and then lifetime F26=no, versus those whose F19 was structurally skipped?
2. **Severity:** how many earlier ages are only one completed year too early, and how many are two or more years too early? This may help characterize the plausibility of age-rounding or recall drift without diagnosing the cause.
3. **Adolescent interview age:** do discrepancies concentrate among respondents who were younger than 15 at the so-called Year 15 interview?
4. **Skip-pattern contradictions:** do explicit Year 15 lifetime-no cases have positive first-sex year/age records, or do adult vaginal-no/any-sex-no records have logically incompatible first-age reports?
5. **Outcome/denominator sensitivity:** how much does the estimate change if definite earlier-age histories are excluded from the baseline-negative eligible domain? This is a *post hoc alternative frame*, not a preferred correction.
6. **Survey design uncertainty:** replicate-weight confidence intervals for the definite-after share and the two extreme classification endpoints.

## 5. Evidence grading

- **Supported**: Among observed FFCWS follow-up respondents who denied intercourse at Year 15, most reported vaginal intercourse by the young-adult interview (~75%).
- **Supported with an important qualification**: Substantial adolescent-to-adult change is reported. A large fraction have later adult-recalled debut ages.
- **Not identified**: Which wave is mistaken in the 49 definite chronology conflicts, or when within their same completed age the 52 ambiguous respondents first had vaginal intercourse.
- **Not assured**: A >50% *confirmed*, post-interview initiation share under all conservative classification choices. The observed strict chronological component is ~48.5% of the original age-15-weighted population, before its sampling CI.
- **Not established**: Current adolescent cohorts follow the same transition, reasons for delay, or complete harmonization with the NSFG's intercourse-with-women definition.

## 6. Primary documentation

- Year 15 Youth Questionnaire, Part F, questions F19–F31: https://ffcws.princeton.edu/sites/g/files/toruqf4356/files/ff_teen_q15.pdf
- Year 22 Young Adult Questionnaire, Part E, E58–E60 and Boxes 22–23: https://ffcws.princeton.edu/sites/g/files/toruqf4356/files/documents/FFCWS%20Y22%20YOUNG%20ADULT%20SURVEY_0.pdf
- Historical measurement-consistency context (not an FFCWS validation): https://pmc.ncbi.nlm.nih.gov/articles/PMC3955171/

**Important limitation:** None of these public documents allows us to decide whether individual participants underreported at Year 15 or misrecalled debut age at Year 22. A gold-standard event-history reconstruction is not available from the published questionnaires alone.
