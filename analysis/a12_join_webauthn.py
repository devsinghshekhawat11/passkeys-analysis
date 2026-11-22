"""Join Ramat et al.'s 111 websites with the WebAuthn options logged by Jannett et al. (USENIX Security 2026).

Input
  data/ramat2026-table1-extracted.csv   (from a11_extract_table1.py)
  data/passkeys-radar-sheet.csv         full PASSKEYS-RADAR evaluation sheet (not committed; downloaded
                                         automatically from the pinned artifact commit if missing)
Output
  data/passkeys-radar-subset.csv         one row per Ramat site: match, availability, and the registration /
                                         sign-in options derived from the logged navigator.credentials calls.
                                         The sheet's attack-result and disclosure columns are NOT carried over.
"""
import csv, json, re, urllib.request
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAMAT = ROOT / "data" / "ramat2026-table1-extracted.csv"
SHEET = ROOT / "data" / "passkeys-radar-sheet.csv"
OUT = ROOT / "data" / "passkeys-radar-subset.csv"
SHEET_URL = ("https://raw.githubusercontent.com/RUB-NDS/state-of-passkeys-artifacts/"
             "7850bc99fdc5123607a77b98f27804c3d3be1fd7/notebooks/sheet.csv")

# Hand-checked matches where the name alone is ambiguous (several rows share a domain or the name differs).
OVERRIDE = {"Australian Government": "my.gov.au", "Air New Zealand": "airnewzealand.com",
            "Bitwarden": "bitwarden.com", "Microsoft": "microsoft.com"}
COSE = {-7: "ES256", -35: "ES384", -36: "ES512", -8: "EdDSA", -257: "RS256", -258: "RS384",
        -259: "RS512", -37: "PS256", -38: "PS384", -39: "PS512", -65535: "RS1", -47: "ES256K"}
# Column positions in the sheet (row 2 holds the sub-headers)
COL = {"name": 0, "domain": 1, "rank": 2, "availability": 5, "confirm": 10, "create": 11, "get": 13,
       "multiple_passkeys": 15, "mode_discoverable": 28, "mode_nondiscoverable": 29,
       "mode_conditional": 30, "signal_api": 31}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def load_sheet():
    if not SHEET.exists():
        print(f"downloading {SHEET_URL}")
        urllib.request.urlretrieve(SHEET_URL, SHEET)
    rows = list(csv.reader(open(SHEET, encoding="utf-8")))
    body = rows[2:]
    j = pd.DataFrame([{k: r[i] for k, i in COL.items()} for r in body])
    j["n"] = j["name"].map(norm)
    j["dn"] = j["domain"].map(lambda d: norm(str(d).split(".")[0]))
    return j


def pick(j, site):
    if site in OVERRIDE:
        m = j[j["domain"] == OVERRIDE[site]]
    else:
        n = norm(site)
        m = j[(j.n == n) | (j.dn == n)]
        if m.empty and len(n) > 3:
            m = j[j.n.str.contains(n) | j.dn.str.contains(n)]
    if m.empty:
        return None
    ok = m[m["availability"] == "TRUE"]
    return (ok if len(ok) else m).iloc[0]


def parse(s):
    try:
        return json.loads(s)
    except (TypeError, ValueError):
        return None


def derive(c, g):
    out = {}
    if c:
        sel = c.get("authenticatorSelection") or {}
        rk = sel.get("residentKey")
        if rk is None and "requireResidentKey" in sel:
            rk = "required(legacy)" if sel["requireResidentKey"] else "discouraged(legacy)"
        algs = [p.get("alg") for p in c.get("pubKeyCredParams", [])]
        out.update(attachment=sel.get("authenticatorAttachment", "unset"), resident_key=rk or "unset",
                   uv_create=sel.get("userVerification", "unset"), attestation=c.get("attestation", "unset"),
                   hints=",".join(c.get("hints", [])) or "unset",
                   algorithms=",".join(COSE.get(a, str(a)) for a in algs),
                   extensions=",".join(sorted((c.get("extensions") or {}).keys())) or "none")
    if g:
        ac = g.get("allowCredentials") or []
        tr = sorted({t for a in ac for t in (a.get("transports") or [])})
        out.update(get_transports=",".join(tr) or ("none-listed" if ac else "empty-allow"),
                   uv_get=g.get("userVerification", "unset"))
    return out


def main():
    ramat = pd.read_csv(RAMAT)
    j = load_sheet()
    recs = []
    for _, r in ramat.iterrows():
        row = pick(j, r.site)
        rec = {"site": r.site, "matched": row is not None}
        if row is not None:
            rec.update(radar_name=row["name"], domain=row["domain"], availability=row["availability"],
                       confirm=row["confirm"], multiple_passkeys=row["multiple_passkeys"],
                       mode_conditional=row["mode_conditional"], mode_nondiscoverable=row["mode_nondiscoverable"],
                       signal_api=row["signal_api"])
            c, g = parse(row["create"]), parse(row["get"])
            rec["has_options"] = c is not None
            rec.update(derive(c, g))
        recs.append(rec)
    df = pd.DataFrame(recs)
    df.to_csv(OUT, index=False)
    print(f"matched {int(df.matched.sum())}/{len(df)} sites; with logged options {int(df.has_options.fillna(False).sum())}")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
