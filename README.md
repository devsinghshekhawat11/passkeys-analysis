# Why Passkey Implementations Diverge

Analysis code, outputs and LaTeX source for our B.Tech final-year research paper on why websites implement passkeys inconsistently, and what FIDO guidance and website developers can change.

**Authors:** Arnav Goel, Neeraj Yadav, Dev Singh Shekhawat
Department of Computer Science and Engineering, Shiv Nadar University
**Supervisor:** Shweta Komari

The paper is in [`paper/passkey-divergence.pdf`](paper/passkey-divergence.pdf).

## What this study does

Ramat et al. (SOUPS 2026) measured passkey implementations on 111 websites against 28 factors and found large inconsistencies. We run a secondary analysis of their published per-site data, combined with a structured coding of five guidance sources (FIDO Alliance Design Guidelines, WebAuthn Level 3, and Google, Apple and Microsoft developer guidance), to explain why websites differ, which differences matter for usability and security, and what should change. We then test those explanations against an independent dataset: the WebAuthn registration and sign-in options that Jannett et al. (USENIX Security 2026) logged on 89 of the same websites.

Main results:

- Factors on which guidance sources agree are implemented more consistently (Spearman ρ = −0.45, p = 0.016; FIDO weighted 70%, the other four sources 7.5% each). The result holds with equal weights (ρ = −0.46), without duplicate or browser-default factors, and when any single source is left out.
- One of the three reported website clusters ("Selective", 20 sites) is a single registration restriction counted four times. The logged options confirm it: 13 of the 14 Selective sites with logged options send `authenticatorAttachment: "platform"`, against 12 of 74 Standard sites (Holm p < 0.001), and 11 of the 14 leave sign-in open to the authenticators that registration refuses.
- The restriction is a deliberate configuration, not a server-library default: sites sharing a library default (go-webauthn, SimpleWebAuthn) leave attachment unset and are no more alike in user experience than random pairs. Finance and e-commerce sites restrict registration more often (45% vs 22%), but that difference is not significant in the logged sample (Holm p = 0.30).
- 70 of 108 websites re-authenticate users neither before a passkey is added nor before one is deleted; in the independent logs, 67% of the joined sites add a passkey without any confirmation.
- Recommendations: 10 changes to the FIDO guidelines, 9 website practices and 4 requests to platform and identity-provider vendors, each graded Strong, Moderate or Weak by its supporting evidence.

We did not visit websites or interview developers. Protocol-level evidence comes from options logged by another team; explanations about intent (for example risk policy) are best-supported readings of correlational evidence.

## Repository layout

```
analysis/   Python analysis scripts and their saved outputs
  factor_analysis.py             per-factor rate, entropy, guidance codes
  factor_stats.csv               per-factor summary table used by later scripts
  a1_cooccurrence_attributes.py  factor co-occurrence (e.g. F09/F10) and site-attribute tests
  a7_cluster_sensitivity.py      cluster re-analysis (Appendix D)
  a9_robustness_lifecycle.py     robustness (unweighted consensus), Benjamini-Hochberg tests, lifecycle exposure, F28 breakdown
  a10_weighted_consensus.py      weighted guidance consensus used in the paper (FIDO 70%, others 7.5%) and its robustness checks
  a11_extract_table1.py          extracts the per-site scores from Table 1 of the Ramat et al. PDF
  a12_join_webauthn.py           joins the 111 sites with PASSKEYS-RADAR logged WebAuthn options
  a13_webauthn_tests.py          tests of the explanations against logged options (Section 4.8, Appendix E)
  *_output.txt                   outputs of each script as reported in the paper
data/       input data (see data/README.md): Ramat scores as CSV, the Table 1 extraction check, and the PASSKEYS-RADAR subset
docs/       h1-attachment-test.md: H1 results and a manual protocol for the remaining gaps
paper/      LaTeX source, figures, build scripts and the compiled PDF
```

## Reproducing the analysis

Requirements: Python 3.10+, `pandas`, `numpy`, `scipy`, `statsmodels`, `scikit-learn`, `openpyxl`, `matplotlib`, `pdfplumber`.

```bash
pip install pandas numpy scipy statsmodels scikit-learn openpyxl matplotlib pdfplumber
cd analysis

# Guidance and co-occurrence analyses (need the Zenodo spreadsheet, see data/README.md)
python3 factor_analysis.py
python3 a9_robustness_lifecycle.py
python3 a10_weighted_consensus.py
python3 a1_cooccurrence_attributes.py ../data/ramat2026-site-scores.xlsx
python3 a7_cluster_sensitivity.py ../data/ramat2026-site-scores.xlsx

# Joined analysis with logged WebAuthn options (runs from the committed CSV files)
python3 a13_webauthn_tests.py > a13_output.txt
# Optional: rebuild the inputs from the sources
python3 a11_extract_table1.py path/to/soups2026-ramat.pdf > a11_output.txt
python3 a12_join_webauthn.py > a12_output.txt      # downloads the full PASSKEYS-RADAR sheet
```

Random procedures (bootstrap, permutation) use a fixed seed (42), so outputs should match the saved `*_output.txt` files.

## Rebuilding the PDF

The paper was written as a document and exported to Markdown (`paper/source-from-doc.md`). `build.py` converts it to LaTeX with pandoc and fills `template.tex`, a two-column layout that approximates the USENIX style. To rebuild it:

```bash
cd paper
python3 figs.py          # regenerates fig1.pdf to fig4.pdf
python3 build.py         # writes paper.tex
pdflatex paper.tex && pdflatex paper.tex
```

Requires pandoc and a TeX Live installation with `mathptmx`.

## Data and citation

- Website-level scores: Ramat et al., SOUPS 2026, supplementary material at https://zenodo.org/records/20709272 (CC BY 4.0). Please cite their paper when using that data.
- Logged WebAuthn options: Jannett et al., "The State of Passkeys", USENIX Security 2026, artifacts at https://github.com/RUB-NDS/state-of-passkeys-artifacts (Apache-2.0). Our subset excludes their attack results.

Guidance coding (M = prescribed 3, S = recommended 2, O = optional 1, A = ambiguous 0.5, X or silent 0) and harm ratings are single-coder judgements by the authors; see Section 3.7 of the paper.
