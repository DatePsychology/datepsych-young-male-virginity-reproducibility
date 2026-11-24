# FFCWS Year15–Year22 Forensic Sexual-History Audit

This is a **local-only** analysis of possible inconsistencies in linked sexual-history reports. The input is the authorized FFCWS/ICPSR Stata microdata. **Do not upload the ICPSR respondent-level data to ChatGPT.** The outputs are aggregated tables with subgroup suppression, suitable for sharing if consistent with your data-use agreement.

## Requirements

- Windows with Python **3.12** (or Python 3.11/3.13 with compatible dependencies). Because Python 3.15 initially caused pandas installation failures in this project, use the known-working **`py -3.12`** invocation.
- One file: `ICPSR_31622\DS0001\31622-0001-Data.dta` from your authorized ICPSR 31622 download (any path is fine).
- Install `numpy` and `pandas` using the supplied `requirements.txt`. **Stata is not required.**

## Step 1 — extract this package

Extract the ZIP. Open PowerShell in the folder containing `forensic_histories.py` and `requirements.txt`.

If the extracted directory is in Downloads, a command similar to this works:

```powershell
cd "C:\Users\Me\Downloads\FFCWS_Forensic_Histories_2026"
```

If Windows extracted an outer folder with the same name, navigate to the inner folder instead.

## Step 2 — install and test

```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 test_forensic_synthetic.py
```

Expected test ending:

`Synthetic forensic tests passed (routing, age-order strata, envelopes, replicate arithmetic).`

The test data are fabricated. They are **not** FFCWS results.

## Step 3 — run on your restricted local dataset

Replace the Stata path with the real location of your `31622-0001-Data.dta`:

```powershell
py -3.12 forensic_histories.py --allwaves "C:\Research\ICPSR_31622\DS0001\31622-0001-Data.dta" --out "C:\Users\Me\Downloads\FFCWS-Forensic-Results" --strict
```

The `--strict` option requires the analysis to reproduce the exact previous case counts: 938 in the target, 697 valid adult vaginal statuses, and 49/52/402 earlier/same/later debut ages. If strict mode stops, **do not discard the warning**: check your data version and file path, then share the error message instead.

## Step 4 — share aggregate outputs

The output folder contains the following eight files:

| File | What it tests |
|---|---|
| `chronology_components.csv` | Replicate-weighted counts and shares for earlier / same / later / missing statuses |
| `classification_envelope.csv` | Strict later-age share and permissive assumptions for ambiguous/missing cases |
| `route_by_chronology.csv` | Whether conflicts differ by F19 current-partner skip route |
| `y15_age_by_chronology.csv` | Whether Year15 interview age relates to contradictions |
| `chronology_severity.csv` | How many recalled ages are one versus two-or-more completed years earlier/later |
| `routing_quality_checks.csv` | Interview logic contradictions and optional F20/F30/F21/F31 skip checks |
| `denominator_sensitivity.csv` | Effect of removing definite earlier-age reports from the initially-negative frame |
| `forensic_metadata.json` | Sample counts, available variables, assumptions, limitations |

Please zip the entire `FFCWS-Forensic-Results` folder and upload that archive. **Do not upload** `.dta`, `.csv` exports of individual persons, or ZIPs containing the original ICPSR files.

## Important statistical qualifications

- Ages are in completed **integer years** at first intercourse (`k7e60`) and months at each interview (`ck6yagem` and `ck7yagem`). When the first-age integer equals completed age at the Year15 interview, event order is **unknown**, not necessarily contradictory.
- The 49 definite earlier ages contradict the previous lifetime-no report **if** adult recollection and age variables are accurate. The data cannot establish which response is incorrect.
- The classification envelope is conditional on treating the retrospective first-age integers as correct. It is **not a sharp bound on the true population initiation rate** under unrestricted measurement error.
- The source weights (`k6natwt`, 33 `k6natwt_rep*` columns) represent the nationally weighted large-city birth cohort, not every US adolescent.
- Point-estimate bounds and replicate-based confidence intervals are distinct; the program supplies normal-approximation 95% replicate CIs, not design-based identification regions jointly covering multiple assumptions.
- Less-than-10 positive subgroup counts are suppressed automatically in all CSVs. No person-level rows, IDs, ages, dates, predictions, or identifying combinations are exported.
- FFCWS asks about vaginal intercourse but not whether each male respondent's vaginal partner was a woman; avoid describing it as perfectly equivalent to NSFG intercourse-with-women.

Read `RESEARCH_FINDINGS.md` for what we can already infer from previously uploaded FFCWS aggregates and the official questionnaires.
