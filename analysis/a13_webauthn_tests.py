"""Test explanations for passkey inconsistency against independently logged WebAuthn options.

Joins Ramat et al.'s factor scores (data/ramat2026-table1-extracted.csv) with the registration and sign-in
options logged by Jannett et al. (data/passkeys-radar-subset.csv, from a12_join_webauthn.py) and tests:

  H1  platform-only registration (authenticatorAttachment: "platform") explains F09/F10 failure
  H2  Selective sites restrict registration but leave sign-in open (F20/F21 partial matches)
  H3  the restriction follows sector risk posture (finance), together with required user verification
  H4  discoverable credentials (residentKey) go with autofill (F18)
  H5  agreement between the two independent audits on overlapping behaviours (Cohen's kappa)
  H6  Signal API use and authenticator-cleanup prompts (F25)
  H7  sites built on the same library default are more alike in UX (permutation test)
  H8  popularity and overall conformity
  plus corroboration checks for Sections 4.5-4.6 of the paper.

Primary tests are Holm-corrected. Output: printed to stdout and saved as a13_output.txt.
"""
import itertools, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, spearmanr
from sklearn.metrics import cohen_kappa_score

ROOT = Path(__file__).resolve().parent.parent
F = [f"F{i:02d}" for i in range(1, 29)]
HSK = ["F09", "F10", "F20", "F21"]
SEED = 42

# Service-type coding by the authors from each site's main business (Appendix E of the paper).
FINANCE = {"Stripe", "Coinbase", "Square Up", "Luno", "Moneybird", "Dinero", "Finom", "PayPal", "Sumup",
           "Money Forward", "Cash App", "Link", "Free Tax USA", "Webull", "Binance", "Marshmallow",
           "Turnkey", "DEXT", "Visma"}
RETAIL = {"Amazon", "Ebay", "Shopify", "Target", "Best Buy", "Shop", "Lowes", "Microcenter", "Migros", "Hard Wax"}
AMBIGUOUS_FINANCE = {"Turnkey", "Marshmallow", "DEXT"}
# Default COSE algorithm lists, read from library source (exact order)
LIBRARY_DEFAULTS = {
    "ES256,ES384,ES512,RS256,RS384,RS512,PS256,PS384,PS512,EdDSA": "go-webauthn",   # CredentialParametersDefault()
    "EdDSA,ES256,RS256": "SimpleWebAuthn",                                           # supportedAlgorithmIDs default
}
AUTH_PROVIDERS = ["Authgear", "Corbado", "FusionAuth", "Hanko.io", "Passage", "Vault Vision"]


def load():
    r = pd.read_csv(ROOT / "data" / "ramat2026-table1-extracted.csv")
    s = pd.read_csv(ROOT / "data" / "passkeys-radar-subset.csv")
    d = r.merge(s, on="site", how="left")
    d["sector"] = np.where(d.site.isin(FINANCE), "finance", np.where(d.site.isin(RETAIL), "retail", "other"))
    return d


def tab2(a, b):
    return pd.crosstab(a, b).reindex(index=[True, False], columns=[True, False], fill_value=0)


def fisher(a, b):
    t = tab2(a, b)
    orr, p = fisher_exact(t.values)
    return {"table [[a&b, a&~b], [~a&b, ~a&~b]]": t.values.tolist(), "odds_ratio": round(float(orr), 3), "p": float(p)}


def kappa(a, b):
    return {"kappa": round(float(cohen_kappa_score(a, b)), 2), "agreement": round(float((a == b).mean()), 3), "n": int(len(a))}


def adjusted_distance(a, b):
    m = (a > 0) & (b > 0)
    return float(np.sqrt(((a[m] - b[m]) ** 2).sum() / m.sum())) if m.sum() else np.nan


def permutation(o, cols, labels, iters=10000):
    X = o[cols].to_numpy(float)
    iu = np.triu_indices(len(o), 1)
    dv = np.array([adjusted_distance(X[i], X[j]) for i, j in zip(*iu)])
    lab = np.asarray(labels)
    rng = np.random.default_rng(SEED)

    def stat(l):
        same = l[iu[0]] == l[iu[1]]
        valid = (l[iu[0]] != "other") & (l[iu[1]] != "other")
        return np.nanmean(dv[same & valid]) - np.nanmean(dv[~same])

    obs = stat(lab)
    null = np.array([stat(rng.permutation(lab)) for _ in range(iters)])
    same = (lab[iu[0]] == lab[iu[1]]) & (lab[iu[0]] != "other")
    return {"within_minus_between": round(float(obs), 3), "p_one_sided": float((null <= obs).mean()),
            "within_pairs": int(same.sum())}


def holm(pvals):
    keys = sorted(pvals, key=pvals.get)
    out, running = {}, 0.0
    for i, k in enumerate(keys):
        running = max(running, min(1.0, (len(keys) - i) * pvals[k]))
        out[k] = running
    return out


def main():
    d = load()
    o = d[d.has_options == True].reset_index(drop=True)
    res = {"sites": len(d), "sites_with_logged_options": len(o),
           "with_options_by_cluster": o.cluster.value_counts().to_dict()}
    P = {}
    o["platform_only"] = o.attachment == "platform"

    # H1
    res["H1_platform_vs_F09_match"] = fisher(o.platform_only, o.F09 == 3)
    res["H1_F09_identical_to_F10_all_111"] = bool((d.F09 == d.F10).all())
    res["H1_platform_by_cluster"] = pd.crosstab(o.cluster, o.platform_only).to_dict()
    res["H1_selective_vs_platform"] = fisher(o.cluster == "Selective", o.platform_only)
    res["H1_restricted_yet_F09_match"] = o[o.platform_only & (o.F09 == 3)].site.tolist()
    res["H1_unrestricted_yet_F09_nonmatch"] = o[~o.platform_only & (o.F09 == 1)].site.tolist()
    res["H1_hints_used"] = o[o.hints != "unset"][["site", "hints", "cluster"]].to_dict("records")
    P["H1 platform-only vs F09"] = res["H1_platform_vs_F09_match"]["p"]
    P["H1 Selective vs platform-only"] = res["H1_selective_vs_platform"]["p"]

    # H2
    sel = o[o.cluster == "Selective"]
    res["H2_selective_signin_request"] = sel.get_transports.value_counts().to_dict()
    res["H2_selective_open_signin_share"] = round(float(sel.get_transports.isin(["empty-allow", "none-listed"]).mean()), 3)
    res["H2_selective_F20_codes"] = sel.F20.value_counts().to_dict()
    res["H2_selective_F21_codes"] = sel.F21.value_counts().to_dict()

    # H3
    fin = o.sector == "finance"
    res["H3_finance_vs_platform"] = fisher(fin, o.platform_only)
    res["H3_finance_vs_uv_required"] = fisher(fin, o.uv_create == "required")
    res["H3_finance_or_retail_vs_platform"] = fisher(o.sector.isin(["finance", "retail"]), o.platform_only)
    keep = ~o.site.isin(AMBIGUOUS_FINANCE)
    res["H3_finance_vs_platform_without_ambiguous_labels"] = fisher(fin[keep], o.platform_only[keep])
    res["H3_selective_by_sector"] = sel.sector.value_counts().to_dict()
    res["H3_sector_counts_with_options"] = o.sector.value_counts().to_dict()
    P["H3 finance vs platform-only"] = res["H3_finance_vs_platform"]["p"]
    P["H3 finance vs UV required"] = res["H3_finance_vs_uv_required"]["p"]
    P["H3 finance+retail vs platform-only"] = res["H3_finance_or_retail_vs_platform"]["p"]

    # H4
    rk = o.resident_key.isin(["required", "preferred", "required(legacy)"])
    res["H4_discoverable_vs_F18"] = fisher(rk, o.F18 == 3)
    P["H4 residentKey vs F18"] = res["H4_discoverable_vs_F18"]["p"]

    # H5
    res["H5_F18_vs_conditional_mediation"] = kappa(o.F18 == 3, o.mode_conditional.astype(str) == "True")
    res["H5_F12_vs_multiple_passkeys"] = kappa(o.F12 >= 2, o.multiple_passkeys.astype(str) == "True")
    conf_any = o.confirm.fillna("").str.contains("Password|Email|SMS|Passkey")
    res["H5_F13_vs_any_confirmation"] = kappa(o.F13 >= 2, conf_any)
    res["H5_F18_disagreements"] = o[(o.F18 == 3) != (o.mode_conditional.astype(str) == "True")].site.tolist()

    # H6
    sig = o.signal_api.astype(str) == "True"
    res["H6_signal_api_sites_and_F25"] = o[sig][["site", "F25"]].to_dict("records")
    res["H6_signal_vs_F25"] = fisher(sig, o.F25 >= 2)

    # H7
    o["library_default"] = o.algorithms.map(LIBRARY_DEFAULTS).fillna("other")
    res["H7_library_default_counts"] = o.library_default.value_counts().to_dict()
    res["H7_library_default_sites"] = {k: o[o.library_default == k].site.tolist() for k in LIBRARY_DEFAULTS.values()}
    res["H7_attachment_by_library_default"] = pd.crosstab(o.library_default, o.attachment).to_dict()
    nohsk = [f for f in F if f not in HSK]
    res["H7_same_library_default_all_factors"] = permutation(o, F, o.library_default.values)
    res["H7_same_library_default_without_HSK_factors"] = permutation(o, nohsk, o.library_default.values)
    sigstr = (o.algorithms.astype(str) + "|" + o.attachment.astype(str) + "|" + o.resident_key.astype(str) + "|" +
              o.uv_create.astype(str) + "|" + o.attestation.astype(str) + "|" + o.extensions.astype(str))
    vc = sigstr.value_counts()
    full = sigstr.where(sigstr.map(vc) >= 2, "other")
    res["H7_identical_configuration_groups"] = {k: o[full == k].site.tolist() for k in full.unique() if k != "other"}
    res["H7_identical_configuration_all_factors"] = permutation(o, F, full.values)
    res["H7_identical_configuration_without_HSK_factors"] = permutation(o, nohsk, full.values)
    drop = o.site != "Dinero"                      # Dinero is owned by Visma and shares its configuration
    o2 = o[drop].reset_index(drop=True)
    f2 = full[drop].reset_index(drop=True)
    vc2 = f2[f2 != "other"].value_counts()
    f2 = f2.where(f2.map(vc2) >= 2, "other")
    res["H7_identical_configuration_without_HSK_without_Dinero"] = permutation(o2, nohsk, f2.values)
    P["H7 same library default"] = res["H7_same_library_default_all_factors"]["p_one_sided"]
    P["H7 identical configuration"] = res["H7_identical_configuration_all_factors"]["p_one_sided"]

    # H8
    d["conformity"] = d[F].apply(lambda r: (r[r > 0] >= 2).mean(), axis=1)
    rank = pd.to_numeric(d["rank"], errors="coerce")
    m = rank.notna()
    rho, p = spearmanr(np.log10(rank[m]), d.conformity[m])
    res["H8_rank_vs_conformity"] = {"rho": round(float(rho), 2), "p": float(p), "n": int(m.sum())}
    P["H8 popularity vs conformity"] = float(p)

    # Corroboration of the paper's own claims
    res["C1_auth_providers_confirmation_step"] = o[o.site.isin(AUTH_PROVIDERS)][["site", "confirm", "F13"]].to_dict("records")
    res["C2_no_confirmation_share_joined_sites"] = round(float((~conf_any).mean()), 3)
    res["C3_selective_sites_without_logged_options"] = d[(d.cluster == "Selective") & (d.has_options != True)][["site", "availability"]].to_dict("records")

    res["holm_adjusted"] = holm(P)
    res["raw_p"] = P
    for k, v in res.items():
        print(f"== {k}\n{json.dumps(v, default=str)}")


if __name__ == "__main__":
    main()
