# Why Passkey Implementations Diverge

Analysis code, outputs and LaTeX source for our B.Tech final-year research paper on why websites implement passkeys inconsistently, and what FIDO guidance and website developers can change.

**Authors:** Arnav Goel, Neeraj Yadav, Dev Singh Shekhawat
Department of Computer Science and Engineering, Shiv Nadar University
**Supervisor:** Shweta Komari

The paper is in [`paper/passkey-divergence.pdf`](paper/passkey-divergence.pdf).

## What this study does

Ramat et al. (SOUPS 2026) measured passkey implementations on 111 websites against 28 factors and found large inconsistencies. We run a secondary analysis of their published per-site data, combined with a structured coding of five guidance sources (FIDO Alliance Design Guidelines, WebAuthn Level 3, and Google, Apple and Microsoft developer guidance), to explain why websites differ, which differences matter for usability and security, and what should change.

Main results:

- Factors on which guidance sources agree are implemented more consistently (Spearman ρ = −0.45, p = 0.016; FIDO weighted 70%, the other four sources 7.5% each). The result holds with equal weights (ρ = −0.46), without duplicate or browser-default factors, and when any single source is left out.
- One of the three reported website clusters ("Selective", 20 sites) is a single registration restriction counted four times; 12 of the 20 are e-commerce or finance sites.
- 70 of 108 websites re-authenticate users neither before a passkey is added nor before one is deleted.
- Recommendations: 10 changes to the FIDO guidelines, 9 website practices and 4 requests to platform vendors.

No websites were visited, no WebAuthn traffic was logged and no developers were interviewed. All explanations are best-supported readings of correlational evidence.

## Repository layout

```
analysis/   Python analysis scripts and their saved outputs
  factor_analysis.py           per-factor rate, entropy, guidance codes
  factor_stats.csv             per-factor summary table used by later scripts
  a1_cooccurrence_attributes.py  factor co-occurrence (e.g. F09/F10) and site-attribute tests
  a7_cluster_sensitivity.py    cluster re-analysis (Appendix D)
  a9_robustness_lifecycle.py   robustness (unweighted consensus), Benjamini-Hochberg tests, lifecycle exposure, F28 breakdown
  a10_weighted_consensus.py    weighted guidance consensus used in the paper (FIDO 70%, others 7.5%) and its robustness checks
  *_output.txt                 output of each script as reported in the paper
data/       where the Ramat et al. dataset goes (not redistributed, see data/README.md)
docs/       h1-attachment-test.md: protocol for a future test of the platform-only registration explanation
paper/      LaTeX source, figures, build scripts and the compiled PDF
```

## Reproducing the analysis

Requirements: Python 3.10+, `pandas`, `numpy`, `scipy`, `statsmodels`, `openpyxl`, `matplotlib`.

```bash
pip install pandas numpy scipy statsmodels openpyxl matplotlib
# 1. Download the dataset (see data/README.md) to data/ramat2026-site-scores.xlsx
cd analysis
python3 factor_analysis.py
python3 a9_robustness_lifecycle.py
python3 a10_weighted_consensus.py
python3 a1_cooccurrence_attributes.py ../data/ramat2026-site-scores.xlsx
python3 a7_cluster_sensitivity.py ../data/ramat2026-site-scores.xlsx
```

Random procedures (bootstrap, permutation) use a fixed seed (42), so outputs should match the saved `*_output.txt` files.

## Rebuilding the PDF

The paper was written as a document and exported to Markdown (`paper/source-from-doc.md`). `build.py` converts it to LaTeX with pandoc and fills `template.tex`, a two-column layout that approximates the USENIX style.

```bash
cd paper
python3 figs.py          # regenerates fig1.pdf, fig2.pdf, fig3.pdf
python3 build.py         # writes paper.tex
pdflatex paper.tex && pdflatex paper.tex
```

Requires pandoc and a TeX Live installation with `mathptmx`.

## Data and citation

Website-level data: Ramat et al., SOUPS 2026, supplementary material at https://zenodo.org/records/20709272. Please cite their paper when using that data.

Guidance coding (M = prescribed 3, S = recommended 2, O = optional 1, A = ambiguous 0.5, X or silent 0) and harm ratings are single-coder judgements by the authors; see Section 3.6 of the paper.
