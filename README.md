# Young Male Virginity — Reproducibility Materials

Code, survey analyses, aggregate results, numerical checks and nine figure reconstructions accompanying the [methodological review](https://datepsych.substack.com/p/are-young-men-starting-sex-later) *Are Young Men Starting Sex Later? What Four Data Sources Can and Can't Tell Us* (24 November 2026).

This is an independent reassessment of [Alexander's 2023 article](https://datepsychology.com/are-27-of-young-men-really-virgins-and-why/), using GSS, NSFG, YRBS and Future of Families and Child Wellbeing Study (FFCWS) survey evidence. The earlier three-survey analyses were run on public-use records. Authorized FFCWS processing was performed locally by the data user; the independent review examined aggregate outputs, not individual records. No respondent microdata are distributed here.

## Contents

| File or directory | Purpose |
|---|---|
| `reproduce_virginity_figures.py` | Regenerates all nine figures from archived aggregate values. |
| `figure_data/` | Plot inputs, including documented qualitative survey measures. |
| `article_figures/` | Exact nine PNGs from the table-free article version. |
| `reproduced_figures/` | Independently regenerated charts; layout may differ. |
| `analyses/gss_nsfg/` | Historical GSS and NSFG replication, survey weights, sensitivity analyses. |
| `analyses/yrbs_nsfg/` | YRBS trend, age-standardization and missingness analyses; NSFG adolescent comparator. |
| `analyses/nsfg_fixed_cohort/` | Retrospective milestone and fixed-cohort analyses. |
| `analyses/nsfg_mode/` | Recovered mode/composition audit code and archived contrasts. |
| `analyses/ffcws_*` | Local-only FFCWS harmonization, weight sensitivity, chronology and final vaginal-specific influence audit. |
| `aggregate_results/` | Final FFCWS local-run aggregates, historical validation, independent review and report. |
| `reports/` | Archived analytical reports and interpretation. |
| `SOURCE_AUDIT.md` | Data provenance, estimands, figure mapping and reproducibility boundaries. |
| `tests/test_reconstruction.py` | Tests against archived aggregate results. |
| `reconstruction_results.txt` | Checked reference output from the root-level tests. |
| `requirements.txt` | Root figure and test dependencies. |

## Reproduce the figures and aggregate checks

Use Python 3.11+ (Python 3.12 is recommended):

```bash
python -m pip install -r requirements.txt
python reproduce_virginity_figures.py
python -m unittest discover -s tests -v
```

No downloads or survey microdata are required for these commands. The figure script writes to `reproduced_figures/`, never `article_figures/`. The root tests verify selected archived aggregate identities and article-critical values; they do not independently rerun the survey estimators.

## Reproduce the survey analyses

Each directory under `analyses/` has its own README, dependencies, and where available the original aggregate output and input hashes. Follow its instructions from that directory. Obtain survey data independently from the official sources. Do not commit respondent records or private local files to a public repository. The FFCWS programs require authorized local access to ICPSR 31622, and any further redistribution of outputs must comply with the applicable terms. Local analysis scripts do not require sending those records to an AI service.

The NSFG mode audit was recovered from the original printed source, with portable file paths and the raw face-to-face contrast added to the output list. It is syntax-checked, not newly rerun on microdata. Some older FFCWS intermediate aggregate files and their original standalone validation scripts are absent; their archived reports and local microdata analysis code remain available. See `SOURCE_AUDIT.md` for precise scope.

## What the evidence supports

- The historical GSS percentages largely reproduce, but the consistently weighted 2018–2021 change is uncertain (−5.87 percentage points, 95% CI −20.44 to +8.70).
- YRBS and pre-redesign NSFG support a historical decline in adolescent sexual initiation. Missingness and changing survey participation limit the inference.
- Historical NSFG age gradients and retrospective milestones show catch-up; the 2022–2023 redesign complicates comparisons. Fixed-cohort discontinuities are diagnostics, not causal mode effects.
- In FFCWS, 75.30% of the 697 observed follow-up respondents reported vaginal intercourse, but only 48.52% of the entire weighted initial domain reported a debut age strictly later than the adolescent interview age. These are different estimands. Weight-capping point estimates were stable, while deletion diagnostics were less precise.
- The evidence does not identify the outcomes of the newest cohorts, the causes of the changes, or their welfare effects.

## Sources

See [SOURCE_AUDIT.md](SOURCE_AUDIT.md) and the reports for the official survey sources, question definitions, methods and limitations. Companion publication: [Revisiting Datepsych](https://datepsych.substack.com/). The specific article URL can be added after publication.

## Redistribution

The archive contains analysis code, aggregate results and generated graphics, not respondent data, third-party articles or raw questionnaires. No open-source license has been assumed on the author's behalf. Verify applicable data-use and redistribution conditions, especially for FFCWS aggregates, and select a code license if desired before publication.
