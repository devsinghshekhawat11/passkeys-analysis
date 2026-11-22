"""Extract the per-site factor scores from Table 1 of Ramat et al. (SOUPS 2026).

Table 1 encodes each website x factor cell as a filled rectangle:
green = match (3), orange = partial match (2), white = non-match (1), black = not applicable (0).
This script reads those rectangles from the PDF and writes
data/ramat2026-table1-extracted.csv (rank, site, cluster, F01..F28).

Usage:  python3 a11_extract_table1.py path/to/soups2026-ramat.pdf
Check:  the extracted matrix reproduces 27 of 28 implementation rates in the paper's Table 2 exactly.
        F28 gives 90% instead of 91%: the printed Table 1 itself shows 84 partial, 11 full and 11 non-match
        cells for F28, while the released spreadsheet (and Table 2) has 83 / 13 / 10. The difference is in
        the source, not the extraction (eight cells differ from the released spreadsheet, all in F28).
        The joined analysis uses the spreadsheet (data/ramat2026-site-scores.csv); this file is a validation.
"""
import sys
from pathlib import Path
import pdfplumber
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "ramat2026-table1-extracted.csv"
FACTORS = [f"F{i:02d}" for i in range(1, 29)]
TABLE_PAGES = (8, 9)            # 0-based page indices of Table 1 in the proceedings PDF
CLUSTER_SIZES = [("Standard", 89), ("Selective", 20), ("Experimental", 2)]  # paper order
TABLE2 = {"F01": 90, "F02": 36, "F03": 43, "F04": 51, "F05": 93, "F06": 25, "F07": 7, "F08": 97,
          "F09": 82, "F10": 82, "F11": 3, "F12": 95, "F13": 30, "F14": 80, "F15": 47, "F16": 53,
          "F17": 84, "F18": 42, "F19": 98, "F20": 96, "F21": 96, "F22": 63, "F23": 93, "F24": 97,
          "F25": 23, "F26": 30, "F27": 69, "F28": 91}


def color_code(c):
    c = tuple(c) if isinstance(c, (list, tuple)) else (c,)
    if len(c) == 1:
        return 1 if c[0] >= 0.99 else (0 if c[0] <= 0.01 else None)
    r, g, b = c[:3]
    if r < 0.1 and 0.4 < g < 0.6 and b < 0.1:
        return 3
    if r > 0.9 and 0.4 < g < 0.6 and b < 0.1:
        return 2
    if min(c[:3]) >= 0.99:
        return 1
    if max(c[:3]) <= 0.01:
        return 0
    return None


def merge_positions(values, gap=3):
    out = []
    for v in sorted(values):
        if not out or v - out[-1] > gap:
            out.append(v)
    return out


def extract(pdf_path):
    records = []
    pdf = pdfplumber.open(pdf_path)
    for pn in TABLE_PAGES:
        p = pdf.pages[pn]
        cells = [r for r in p.rects if 12 < (r["x1"] - r["x0"]) < 16
                 and 7.5 < (r["bottom"] - r["top"]) < 9 and r.get("fill")]
        legend_top = min(w["top"] for w in p.extract_words() if w["text"].startswith("Legend"))
        cells = [r for r in cells if r["top"] < legend_top - 2]
        cols = merge_positions({round(r["x0"], 1) for r in cells})
        assert len(cols) == 28, (pn, len(cols))
        rows = merge_positions({round(r["top"], 1) for r in cells})
        words = p.extract_words(keep_blank_chars=True, x_tolerance=1.5)
        left = [w for w in words if w["x1"] < cols[0] - 1]
        for rt in rows:
            label = " ".join(w["text"] for w in sorted(
                (w for w in left if abs((w["top"] + w["bottom"]) / 2 - (rt + 4.2)) < 3.5),
                key=lambda w: w["x0"])).strip()
            vals = []
            for cx in cols:
                codes = {color_code(h["non_stroking_color"]) for h in cells
                         if abs(h["x0"] - cx) < 3 and abs(h["top"] - rt) < 3} - {None}
                vals.append(codes.pop() if len(codes) == 1 else None)
            if label:
                records.append([label] + vals)
    df = pd.DataFrame(records, columns=["label"] + FACTORS)
    m = df["label"].str.extract(r"^\s*(\d+|Unranked)\s*:\s*(.+)$")
    df.insert(0, "rank", m[0])
    df.insert(1, "site", m[1].str.strip())
    df = df.drop(columns="label")
    df.insert(2, "cluster", sum(([name] * n for name, n in CLUSTER_SIZES), []))
    return df


def rate(s):
    s = s[s > 0]
    return round(100 * (s >= 2).mean())


if __name__ == "__main__":
    df = extract(sys.argv[1])
    assert len(df) == 111 and df[FACTORS].notna().all().all()
    df.to_csv(OUT, index=False)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(df)} sites")
    print("factor  extracted  paper")
    for f in FACTORS:
        print(f"{f}     {rate(df[f]):>3}%      {TABLE2[f]:>3}%{'  <-- differs' if rate(df[f]) != TABLE2[f] else ''}")
    for name, _ in CLUSTER_SIZES:
        sub = df[df.cluster == name]
        print(name, "mean rate", round(sum(rate(sub[f]) if (sub[f] > 0).any() else 0 for f in FACTORS) / 28))
