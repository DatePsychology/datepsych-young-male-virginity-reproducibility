# NSFG mode and composition audit

Recovered from the original printed analysis source in the research log. The input and output paths are portable, and the raw face-to-face versus historical contrast has been added to the output list using the same paired bootstrap estimates. The core estimator and seed (400 replicates, 20261123) are unchanged. This recovered version has been syntax-checked but not rerun on the original records in this release.

Obtain `2017_2019_MaleData.dat`, its `2017_2019_MaleSetup*.dct` dictionary, and `NSFG-2022-2023-MaleRespPUFData.zip` from CDC. Put them in `input/` here or set `NSFG_DATA_ROOT`. Install the dependencies in `requirements.txt`, then run `python run_mode_audit.py`. Output goes to `output/`. Mode assignment is observational; the bootstrap intervals are exploratory. See the root SOURCE_AUDIT for reported estimates.
