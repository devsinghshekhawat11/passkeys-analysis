# Data

## 1. Ramat et al. per-site scores (SOUPS 2026)

The guidance and co-occurrence analyses (`factor_analysis.py`, `a1`, `a7`, `a9`) use the per-website scores published by Ramat et al. as supplementary material (CC BY 4.0):
https://zenodo.org/records/20709272

Download the per-site score spreadsheet from the Zenodo record and save it as:

```
data/ramat2026-site-scores.xlsx
```

Expected layout: one row per website (111 rows), the first five columns are site metadata (including `Category`), and the next 28 columns are the factor scores F01 to F28 (0 = not applicable, 1 = no match, 2 = partial match, 3 = full match).

`analysis/factor_stats.csv` is the per-factor summary derived from that file (implementation rate, normalised entropy, guidance codes). The guidance-consensus scripts (`a10_weighted_consensus.py`) only need this CSV.

### `ramat2026-table1-extracted.csv` (committed)

The same 111 x 28 scores, extracted from the coloured cells of Table 1 in the published PDF by `analysis/a11_extract_table1.py`, plus each site's popularity rank and cluster. The joined analysis (`a12`, `a13`) uses this file, so it runs without the Zenodo download. Columns: `rank`, `site`, `cluster`, `F01`..`F28`.

It reproduces 27 of the 28 implementation rates in the paper's Table 2 exactly. For F28 it gives 90% instead of 91%: the printed Table 1 shows 84 partial, 11 full and 11 non-match cells, while the spreadsheet behind Table 2 has 83 / 13 / 10. The difference is in the source, not in the extraction. Credit: Ramat, Kartchner, Clark and Seamons, SOUPS 2026 (CC BY 4.0).

## 2. Logged WebAuthn options: PASSKEYS-RADAR (Jannett et al., USENIX Security 2026)

### `passkeys-radar-subset.csv` (committed)

One row per Ramat site, built by `analysis/a12_join_webauthn.py` from the PASSKEYS-RADAR evaluation sheet (`notebooks/sheet.csv` at commit `7850bc9` of https://github.com/RUB-NDS/state-of-passkeys-artifacts, Apache-2.0). Columns:

| Column | Meaning |
| --- | --- |
| `site`, `matched`, `radar_name`, `domain`, `availability` | The match and whether Jannett et al. could analyse the site (`TRUE` = analysed) |
| `confirm` | Extra confirmation required to add a passkey (`-`/`--` = none; otherwise Password, Email, SMS, ...) |
| `multiple_passkeys`, `mode_conditional`, `mode_nondiscoverable`, `signal_api` | Observed behaviours (multiple passkeys allowed, conditional mediation/autofill, non-discoverable or 2FA mode, Signal API use) |
| `has_options` | Whether `navigator.credentials.create()` options were logged |
| `attachment`, `hints`, `resident_key`, `uv_create`, `attestation`, `algorithms`, `extensions` | Derived from the logged registration options |
| `get_transports`, `uv_get` | Derived from the logged sign-in options (`empty-allow` = empty `allowCredentials`; `none-listed` = credentials listed without transports) |

The subset deliberately **omits** the sheet's attack-result, responsible-disclosure and raw request columns. Credit: Jannett, Mayer, Westers, Mladenov, Mainka and Schwenk, "The State of Passkeys", USENIX Security 2026 (Apache-2.0).

### `passkeys-radar-sheet.csv` (not committed)

The full evaluation sheet. `a12_join_webauthn.py` downloads it automatically from the pinned commit if it is missing; it is only needed to rebuild the subset.
