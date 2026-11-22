# Data

The analysis uses the per-website scores published by Ramat et al. (SOUPS 2026) as supplementary material:
https://zenodo.org/records/20709272

We do not redistribute that file here. Download the per-site score spreadsheet from the Zenodo record and save it as:

```
data/ramat2026-site-scores.xlsx
```

Expected layout: one row per website (111 rows), the first five columns are site metadata (including `Category`), and the next 28 columns are the factor scores F01 to F28 (0 = not applicable, 1 = no match, 2 = partial match, 3 = full match).

`analysis/factor_stats.csv` is the per-factor summary derived from that file (implementation rate, normalised entropy, guidance codes). The guidance-consensus scripts (`a10_weighted_consensus.py`) only need this CSV.
