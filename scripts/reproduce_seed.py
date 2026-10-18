"""Reproduce the seed paper's figures from its own data, with the grammar templates.

WHY THIS SCRIPT IS THE TEST OF THE TEMPLATE LAYER
    "复现并形成可视化模板代码" -- the templates are only worth having if they can carry a real
    paper's figures, not if they can draw a demo. The seed paper (NHB 2026, "The growing
    concentration of national influence in global science and its impact on future research")
    ships its published figures, its analysis code and its raw tables. So the test is concrete:

        published statistic  ==?  statistic recomputed from the raw data through a template

    A reproduction that looks right but does not reproduce the stated correlation is a drawing,
    not a reproduction. Every panel below reports the delta.

WHAT IS REPRODUCED, AND WHAT IS NOT
    Fig 1a, 1b   ranked share of term papers by country; log-log density of terms.
    Fig 3a,3b    Gini of country centrality over time, attributional and discursive.
    Fig 3c       mean ± s.e.m. centrality by core/periphery, both networks.
    Fig 5        2x2 panes of relative influence between core and periphery.
    Fig 7        2x2 panes of national-signature mimicry (cosine similarity).
    NOT Fig 2    the QAP regression coefficients are not in the published data package.
    NOT Fig 4    same construction as Fig 3 from relative influence; the centrality file is
                 derived here, so it is a one-line extension -- left out to keep the run short.
    NOT Fig 6    the arc diagram and the region matrix need a country -> region mapping that
                 the package does not include (the R recipe gets it from `raster::ccodes` plus
                 a custom UNREGION1 table). Imitating it without the mapping would be invention.

HOW THE HEAVY STEP WORKS
    The attributional edgelist is 639 MB. It is read in chunks with only the four needed columns,
    filtered to the paper's own 10,046 censored terms, and aggregated to (influencer, influenced,
    year). The aggregation is cached as a gzip so the panels can be rebuilt without the pass;
    the cache is a regenerable intermediate and is not versioned.

DATA LOCATIONS (read-only)
    Seeds/0001/dataverse_files/            the paper's recipe, small tables, censored term list
    E:/2026-AI4S/dataverse_cache/0001/     the raw 1.57 GB of CSV, moved out of the repository to
                                          keep it lean (see Seeds/README.md)
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from figpipe import audit, composite, grammar, layout  # noqa: E402

SEED = ROOT / "Seeds" / "0001"
DATA_DIRS = [pathlib.Path("E:/2026-AI4S/dataverse_cache/0001/dataverse_files"),
             SEED / "dataverse_files"]
DERIVED = ROOT / "corpus" / "seed" / "derived"
CACHE = ROOT / "corpus" / "seed" / "cache"
OUT = ROOT / "templates" / "seed"
REPORT = OUT / "report.json"

YEAR_MIN, YEAR_MAX = 1990, 2013
WIDTH_MM = 183.0

#: The seed's own core-country list (Step_X6_R_...L.R, lines 17-44). It is DATA of the seed,
#: not a heuristic: the paper classifies a country as core when it is in this list.
CORE_COUNTRIES = {
    "US", "GB", "CN", "DE", "JP", "AU", "AT", "BE", "CA", "DK", "FI", "FR", "IS", "IE",
    "IT", "IL", "NL", "NZ", "NO", "PT", "SG", "KR", "ES", "SE", "CH", "TW",
}

#: ISO2 -> name for the countries that appear in the top-20 panel. The seed's R uses
#: `raster::ccodes()`, which is not vendored here; a code with no entry falls back to the code
#: itself rather than to a guessed name.
ISO2_NAME = {
    "US": "United States", "GB": "United Kingdom", "CN": "China", "DE": "Germany",
    "JP": "Japan", "AU": "Australia", "AT": "Austria", "BE": "Belgium", "CA": "Canada",
    "DK": "Denmark", "FI": "Finland", "FR": "France", "IS": "Iceland", "IE": "Ireland",
    "IT": "Italy", "IL": "Israel", "NL": "Netherlands", "NZ": "New Zealand",
    "NO": "Norway", "PT": "Portugal", "SG": "Singapore", "KR": "South Korea",
    "ES": "Spain", "SE": "Sweden", "CH": "Switzerland", "TW": "Taiwan", "IN": "India",
    "BR": "Brazil", "RU": "Russia", "PL": "Poland", "TR": "Turkey", "ZA": "South Africa",
    "MX": "Mexico", "AR": "Argentina", "CL": "Chile", "GR": "Greece", "HU": "Hungary",
    "CZ": "Czechia", "RO": "Romania", "UA": "Ukraine", "MY": "Malaysia", "TH": "Thailand",
    "ID": "Indonesia", "PK": "Pakistan", "IR": "Iran", "EG": "Egypt", "NG": "Nigeria",
    "SA": "Saudi Arabia", "AE": "United Arab Emirates", "HK": "Hong Kong", "CY": "Cyprus",
    "EE": "Estonia", "LV": "Latvia", "LT": "Lithuania", "SI": "Slovenia", "SK": "Slovakia",
    "HR": "Croatia", "RS": "Serbia", "BG": "Bulgaria", "CO": "Colombia", "PE": "Peru",
}

#: The statistics the paper prints in its captions. The reproduction is judged against them.
PUBLISHED = {
    "fig1b_r": 0.78,
    "fig3_gini_r": {"Attributional": 0.88, "Discursive": 0.86},
    "fig3_centrality_r": {"Attributional": {"Core": 0.98, "Periphery": 0.87},
                          "Discursive": {"Core": 0.99, "Periphery": 0.86}},
    "fig5_r": {"Core→Core": 0.88, "Core→Periphery": 0.47,
               "Periphery→Core": -0.43, "Periphery→Periphery": 0.43},
    "fig7_r": {"Core→Core": 0.96, "Core→Periphery": 0.66,
               "Periphery→Core": -0.62, "Periphery→Periphery": -0.69},
}


#: A reproduction is only as complete as the LAYER it reaches. Saying "reproduced" without a
#: layer is an unfalsifiable claim: this work re-ran the authors' transformation chain on their
#: published aggregate tables; it did NOT rebuild those tables from the OpenAlex snapshot.
REPRODUCTION_LAYERS = {
    "L0 data construction": (
        "NOT reproduced. The authors built the tables from a ~240M-work OpenAlex snapshot via "
        "AWS Athena SQL, four key-phrase extractors and a 10-year citation window. This work "
        "starts from the published OUTPUT_* aggregates and the authors' own 10,046-term censored "
        "list, so an error in that construction would be INHERITED, not detected."),
    "L1 transformation": (
        "Reproduced. The R recipe was re-implemented in Python: sum weights per dyad-year, "
        "filter to the censored terms, outer-join the two networks, per-year z-scoring, "
        "relative influence as the difference, per-country centrality, Gini, mean +/- s.e.m. "
        "This is a re-implementation of the SAME formulas, not an independent derivation: "
        "where the authors' code is wrong, the reproduction is wrong the same way."),
    "L2 figures": (
        "Partially reproduced: 13 of the paper's 18 panels (Fig 1a/1b 2, Fig 3a/b/c 3, Fig 5 4, "
        "Fig 7 4). Fig 2 (QAP permutations) is not in the package; Fig 4 was omitted (same "
        "construction as Fig 3); Fig 6 needs a country->region mapping the package does not "
        "ship."),
    "L3 typography": (
        "Deliberately different. The originals are ggplot2 figures rendered by the journal "
        "(8x8 in, ~9-10 pt, grey grid, red/green diverging); the reproductions follow Nature's "
        "submission spec (183 mm, 5-7 pt, Okabe-Ito, red-blue diverging). The statistics agree; "
        "the graphic language does not, and must not be read as fidelity."),
}

#: Per-figure provenance of the reproduction claim: panels, estimator, inputs, deviations.
FIGURE_META = {
    "fig1_term_papers_and_density": {
        "published_panels": 2, "reproduced_panels": 2,
        "layer": "L1+L2 (L0 not reproduced)",
        "estimator": ("Fig 1a: share of unique (term, year, influencer) rows per country; "
                      "Fig 1b: Pearson r on log10(n_papers), log10(n_cites)"),
        "inputs": ["OUTPUT_List_of_Censored_Terms_2024_03_19.csv",
                   "OUTPUT_Python_MultiPaper_Discursive_Influence_2024_03_19.csv",
                   "OUTPUT_Python_MultiPaper_Number_of_Cites_per_Influencer_Paper_"
                   "Attributional_Influence_2024_03_19.csv"],
        "deviations": [
            "Fig 1b shows marginal histograms on BOTH axes in the paper; the reproduction has "
            "the top marginal only, because the right side is used by the colour bar.",
            "Fig 1a country names come from a small vendored ISO2 table; the authors use "
            "raster::ccodes(), which is not in the package.",
            "Fig 1b annotation quotes the log-scale r (0.775) to match the drawn scale; the "
            "raw-scale r is 0.83. See the Fig 1b discrepancy record."],
    },
    "fig3_centrality_and_gini": {
        "published_panels": 3, "reproduced_panels": 4,
        "layer": "L1+L2 (L0 not reproduced)",
        "estimator": "Pearson r of yearly Gini / yearly mean centrality against year",
        "inputs": ["OUTPUT_Python_MultiPaper_Attributional_Influence_2024_03_19.csv",
                   "OUTPUT_Python_MultiPaper_Discursive_Influence_2024_03_19.csv"],
        "deviations": [
            "The paper letters panel c once and splits it into two facets; the reproduction "
            "uses letters c and d, so it carries one more letter.",
            "Published facets use free_y; the reproduction shares one y scale per network.",
            "The published panels carry a light grey grid; the reproduction has no gridlines "
            "(figpipe style rule)."],
    },
    "fig5_relative_influence": {
        "published_panels": 4, "reproduced_panels": 4,
        "layer": "L1+L2 (L0 not reproduced)",
        "estimator": ("Pearson r of yearly mean relative influence against year, per "
                      "core/periphery dyad class"),
        "inputs": ["OUTPUT_Python_MultiPaper_Attributional_Influence_2024_03_19.csv",
                   "OUTPUT_Python_MultiPaper_Discursive_Influence_2024_03_19.csv"],
        "deviations": [
            "Pane titles shortened from three lines to one.",
            "The loess band is APPROXIMATED (tricube local linear, global residual variance); "
            "it is not ggplot2's loess variance -- stated in drawlib.",
            "Directional labels ('greater discursive/attributational influence') are placed by "
            "eye from the published figure, not measured."],
    },
    "fig7_national_signature_mimicry": {
        "published_panels": 4, "reproduced_panels": 4,
        "layer": "L1+L2 (L0 not reproduced)",
        "estimator": "Pearson r of yearly mean cosine similarity against year, n=19 (1995-2013)",
        "inputs": ["OUTPUT_Python_HNB_RR1_National_Signature_Influence_2024_03_19.csv"],
        "deviations": [
            "Pane titles shortened from three lines to one.",
            "Marker and fit colours matched to the published panel (black points, blue fit)."],
    },
}

#: Statistics whose ESTIMATOR could not be fully resolved from the package. A reproduction that
#: silently switches estimator to hit a published number is not a reproduction, so the ambiguity
#: is recorded as data rather than hidden behind the matching value.
DISCREPANCIES = [
    {"figure": "Fig 1b", "statistic": "Pearson r, term papers vs attributional papers",
     "raw_scale": 0.83, "log_scale": 0.775, "published": 0.78,
     "resolution": ("UNRESOLVED: published 0.78 matches the log-scale value and the axes are "
                    "log10, but the authors' ggpubr::stat_cor call reads as raw-scale. Both "
                    "values are reported; the figure quotes the drawn scale."),
     "risk": ("if the authors computed raw-scale r, then 0.78 and 0.775 agree by coincidence "
              "and the gap is real")},
]


# --------------------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------------------

def source(name: str) -> pathlib.Path:
    """Resolve one input file across the two read-only data locations."""
    for d in DATA_DIRS:
        p = d / name
        if p.is_file():
            return p
    raise FileNotFoundError(f"{name} not found in {[str(d) for d in DATA_DIRS]}")


def censored_terms() -> set[str]:
    p = source("OUTPUT_List_of_Censored_Terms_2024_03_19.csv")
    return set(pd.read_csv(p, encoding="utf-8")["Term"].astype(str))


def _sha256(path: pathlib.Path, max_bytes: int = 50 * 1024 * 1024) -> str:
    """Content hash for provenance; only files up to `max_bytes` are hashed in full."""
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as fh:
        read = 0
        while read < max_bytes:
            chunk = fh.read(min(4 * 1024 * 1024, max_bytes - read))
            if not chunk:
                break
            h.update(chunk)
            read += len(chunk)
    return h.hexdigest() if path.stat().st_size <= max_bytes else h.hexdigest() + "+sampled"


def _provenance(names: list[str]) -> list[dict]:
    out = []
    for n in names:
        p = source(n)
        st = p.stat()
        out.append({"file": n, "bytes": st.st_size, "mtime_ns": st.st_mtime_ns,
                    "sha256_or_sample": _sha256(p)})
    return out


# --------------------------------------------------------------------------------------
# Derivation
# --------------------------------------------------------------------------------------

def _sum_edgelist(name: str, value_col: str, terms: set[str],
                  chunksize: int = 3_000_000) -> pd.DataFrame:
    """(Influencer, Influenced, Year) -> sum(value_col), filtered to the censored terms.

    THE CHUNKED PASS EXISTS BECAUSE THE FILE IS 639 MB. Reading it whole would work on this
    machine and fail on a smaller one, and the aggregation is associative, so the chunk sum is
    the same number as the whole-file sum -- verified against the published correlations.
    """
    parts = []
    for chunk in pd.read_csv(source(name), usecols=["Term", "Year", "Influencer",
                                                    "Influenced", value_col],
                             encoding="utf-8", chunksize=chunksize,
                             dtype={"Influencer": "string", "Influenced": "string"}):
        chunk = chunk[chunk["Term"].astype(str).isin(terms)]
        if chunk.empty:
            continue
        parts.append(chunk.groupby(["Influencer", "Influenced", "Year"],
                                   observed=True)[value_col].sum())
    if not parts:
        raise ValueError(f"{name}: no rows survived the censored-term filter")
    agg = pd.concat(parts)
    return agg.groupby(level=[0, 1, 2]).sum().reset_index()


def influence_edges(refresh: bool = False) -> pd.DataFrame:
    """The paper's Influence_df: dyad-year attributional and discursive influence, z-scored.

    Mirrors Step_X6_R_...L.R lines 95-128: sum the weights per dyad-year within each network,
    outer-join, zero-fill, drop self-links, z-score each network within each year (R `scale()`),
    and take relative influence as the difference of the two z-scores.
    """
    cache = CACHE / "influence_edges.csv.gz"
    if cache.is_file() and not refresh:
        return pd.read_csv(cache, encoding="utf-8")
    terms = censored_terms()
    print(f"  censored terms: {len(terms)}")
    print("  aggregating the discursive edgelist ...")
    disc = _sum_edgelist("OUTPUT_Python_MultiPaper_Discursive_Influence_2024_03_19.csv",
                         "Weight", terms)
    disc = disc.rename(columns={"Weight": "Discursive_Influence"})
    print("  aggregating the attributional edgelist (639 MB, chunked) ...")
    attr = _sum_edgelist("OUTPUT_Python_MultiPaper_Attributional_Influence_2024_03_19.csv",
                         "Influenced_Weights", terms)
    attr = attr.rename(columns={"Influenced_Weights": "Attributional_Influence"})
    key = ["Influencer", "Influenced", "Year"]
    df = disc.merge(attr, on=key, how="outer").fillna(0.0)
    df = df[df["Influencer"] != df["Influenced"]]
    df = df[(df["Year"] >= YEAR_MIN) & (df["Year"] <= YEAR_MAX)].copy()
    for col in ("Discursive_Influence", "Attributional_Influence"):
        mu = df.groupby("Year")[col].transform("mean")
        sd = df.groupby("Year")[col].transform("std")          # pandas/R both use ddof=1
        df[col + "_z"] = (df[col] - mu) / sd
    df = df.dropna(subset=["Discursive_Influence_z", "Attributional_Influence_z"])
    df["Relative_Influence"] = df["Discursive_Influence_z"] - df["Attributional_Influence_z"]
    df["sender_cp"] = np.where(df["Influencer"].isin(CORE_COUNTRIES), "Core", "Periphery")
    df["receiver_cp"] = np.where(df["Influenced"].isin(CORE_COUNTRIES), "Core", "Periphery")
    CACHE.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache, index=False, compression="gzip")
    print(f"  cached {len(df):,} dyad-years -> {cache.relative_to(ROOT)}")
    return df


def _per_year(edges: pd.DataFrame) -> pd.DataFrame:
    """Mean ± s.e.m. of relative influence per sender→receiver class and year (Fig. 5)."""
    g = (edges.groupby(["Year", "sender_cp", "receiver_cp"], observed=True)
         ["Relative_Influence"]
         .agg(mean="mean", sd="std", n="size").reset_index())
    g["se"] = g["sd"] / np.sqrt(g["n"])
    return g


def _centrality(edges: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Country centrality, z-scored within year; and the yearly Gini of it (Fig. 3)."""
    c = (edges.groupby(["sender_cp", "Influencer", "Year"], observed=True)
         [["Discursive_Influence", "Attributional_Influence", "Relative_Influence"]]
         .sum().reset_index().rename(columns={"sender_cp": "cp", "Influencer": "country"}))
    for col in ("Discursive_Influence", "Attributional_Influence"):
        mu = c.groupby("Year")[col].transform("mean")
        sd = c.groupby("Year")[col].transform("std")
        c[col] = (c[col] - mu) / sd
    g = (c.groupby(["cp", "Year"], observed=True)
         [["Discursive_Influence", "Attributional_Influence"]]
         .agg(["mean", "std", "count"]))
    rows = []
    for (cp, year), r in g.iterrows():
        for network, col in (("Attributional", "Attributional_Influence"),
                             ("Discursive", "Discursive_Influence")):
            rows.append({"cp": cp, "Year": year, "network": network,
                         "mean": r[(col, "mean")],
                         "se": r[(col, "std")] / np.sqrt(r[(col, "count")]),
                         "n": r[(col, "count")]})
    central = pd.DataFrame(rows)

    def gini(v):
        v = np.sort(np.asarray(v, dtype=float))
        n = len(v)
        if n == 0 or v.sum() == 0:
            return float("nan")
        idx = np.arange(1, n + 1)
        return float((2 * (idx * v).sum()) / (n * v.sum()) - (n + 1) / n)

    ginis = []
    for year, part in c.groupby("Year"):
        for network, col in (("Attributional", "Attributional_Influence"),
                             ("Discursive", "Discursive_Influence")):
            v = part[col].to_numpy(dtype=float)
            ginis.append({"Year": year, "network": network,
                          "gini": gini(v - np.nanmin(v))})
    return central, pd.DataFrame(ginis)


def _fig7_panes() -> pd.DataFrame:
    """Mimicry (cosine similarity) per sender→receiver class and year (Fig. 7)."""
    hnb = pd.read_csv(source("OUTPUT_Python_HNB_RR1_National_Signature_Influence_2024_03_19.csv"),
                      encoding="utf-8")
    hnb = hnb[hnb["Influence_1"] != 1]
    g = (hnb.groupby(["Year", "Sender_Core_Periphery", "Receiver_Core_Periphery"],
                     observed=True)["Influence_1"]
         .agg(mean="mean", sd="std", n="size").reset_index()
         .rename(columns={"Sender_Core_Periphery": "sender_cp",
                          "Receiver_Core_Periphery": "receiver_cp"}))
    g["se"] = g["sd"] / np.sqrt(g["n"])
    return g


def _fig1_panels() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Term-paper share by country (Fig. 1a) and per-term counts (Fig. 1b)."""
    terms = censored_terms()
    print("  computing the country share of term papers ...")
    disc = pd.read_csv(source("OUTPUT_Python_MultiPaper_Discursive_Influence_2024_03_19.csv"),
                       usecols=["Term", "Year", "Influencer"], encoding="utf-8")
    disc = disc[disc["Term"].astype(str).isin(terms)]
    pairs = disc.drop_duplicates(subset=["Term", "Year", "Influencer"])
    counts = pairs["Influencer"].value_counts().rename_axis("iso2").reset_index(name="count")
    counts["percent"] = counts["count"] / counts["count"].sum()
    counts["name"] = [ISO2_NAME.get(c, c) for c in counts["iso2"]]
    print("  computing per-term paper and citation counts ...")
    stats = pd.read_csv(
        source("OUTPUT_Python_MultiPaper_Number_of_Cites_per_Influencer_Paper_"
               "Attributional_Influence_2024_03_19.csv"),
        usecols=["Term", "Year", "Influencer_Paper_ID",
                 "Number_of_Citations_per_Influencer_Paper"], encoding="utf-8")
    stats = stats[stats["Term"].astype(str).isin(terms)]
    per_term = (stats.groupby("Term", observed=True)
                .agg(n_papers=("Influencer_Paper_ID", "size"),
                     n_cites=("Number_of_Citations_per_Influencer_Paper", "sum"))
                .reset_index())
    per_term = per_term[(per_term["n_papers"] > 0) & (per_term["n_cites"] > 0)]
    return counts, per_term


def derive(refresh: bool = False) -> dict:
    """Compute every panel dataset and write it under corpus/seed/derived/."""
    DERIVED.mkdir(parents=True, exist_ok=True)
    edges = influence_edges(refresh=refresh)

    fig5 = _per_year(edges)
    central, ginis = _centrality(edges)
    fig7 = _fig7_panes()
    fig1a, fig1b = _fig1_panels()

    files = {
        "fig5_relative_influence": fig5,
        "fig3_centrality": central,
        "fig3_gini": ginis,
        "fig7_mimicry": fig7,
        "fig1a_country_share": fig1a,
        "fig1b_term_counts": fig1b,
    }
    written = {}
    for name, df in files.items():
        p = DERIVED / f"{name}.csv"
        df.to_csv(p, index=False)
        written[name] = {"file": str(p.relative_to(ROOT)), "rows": int(len(df))}
        print(f"  derived {name:<26} {len(df):>7,} rows")
    manifest = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "years": [YEAR_MIN, YEAR_MAX],
        "core_countries": sorted(CORE_COUNTRIES),
        "inputs": _provenance([
            "OUTPUT_List_of_Censored_Terms_2024_03_19.csv",
            "OUTPUT_Python_MultiPaper_Discursive_Influence_2024_03_19.csv",
            "OUTPUT_Python_MultiPaper_Attributional_Influence_2024_03_19.csv",
            "OUTPUT_Python_MultiPaper_Number_of_Cites_per_Influencer_Paper_"
            "Attributional_Influence_2024_03_19.csv",
            "OUTPUT_Python_HNB_RR1_National_Signature_Influence_2024_03_19.csv",
        ]),
        "derived": written,
        "note": ("Computed by scripts/reproduce_seed.py from the seed package. The edgelist "
                 "aggregation is cached under corpus/seed/cache/ (regenerable, not versioned)."),
    }
    (DERIVED / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return files


# --------------------------------------------------------------------------------------
# Panels
# --------------------------------------------------------------------------------------

def _pearson(x, y) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    return float(np.corrcoef(x, y)[0, 1])


def _r_text(r: float, n: int) -> str:
    return f"r = {r:.2f}, n = {n}"


def _pane_panels(data: pd.DataFrame, order: list[tuple[str, str]], ylabel: str,
                 xlabel: str, fit: str, band: str, reference: float | None,
                 connect: bool, notes_for=None, annotate_for=None,
                 palette=None, fit_color=None, xticks=None) -> list:
    """Four intents, one per sender→receiver class, from the seed's pane order."""
    panels = []
    for i, (sender, receiver) in enumerate(order):
        part = data[(data["sender_cp"] == sender) & (data["receiver_cp"] == receiver)]
        part = part.sort_values("Year")
        if part.empty:
            raise ValueError(f"no rows for {sender}→{receiver}")
        r = _pearson(part["Year"], part["mean"])
        notes = notes_for(r, len(part)) if notes_for else [
            {"x": 0.04, "y": 0.95, "text": _r_text(r, len(part)), "ha": "left", "va": "top"}]
        kw = dict(x="Year", y="mean", fit=fit, band=band, reference=reference,
                  connect=connect, notes=notes, legend=False,
                  title=f"{sender} → {receiver}",
                  xlabel=xlabel if i >= 2 else "",
                  ylabel=ylabel if i % 2 == 0 else "",
                  palette=palette, fit_color=fit_color, xticks=xticks)
        panels.append(grammar.panel("trend_with_uncertainty", part, **kw))
    return panels


def plate_fig7() -> tuple[list, dict]:
    data = pd.read_csv(DERIVED / "fig7_mimicry.csv", encoding="utf-8")
    order = [("Core", "Core"), ("Core", "Periphery"),
             ("Periphery", "Core"), ("Periphery", "Periphery")]
    panels = _pane_panels(data, order, ylabel="Mimicry\n(cosine similarity)", xlabel="Year",
                          fit="lm", band="fit", reference=None, connect=True,
                          palette=["#1f1f1f"], fit_color="#0072b2",
                          xticks=[1995, 2000, 2005, 2010])
    computed = {}
    for sender, receiver in order:
        part = data[(data["sender_cp"] == sender) & (data["receiver_cp"] == receiver)]
        computed[f"{sender}→{receiver}"] = round(_pearson(part["Year"], part["mean"]), 3)
    return panels, {"computed": computed,
                    "layout": {"columns": 2.0, "height_mm": 168.0,
                               "sharex": True, "sharey": True, "letters": False,
                               "margins": {"bottom": 13.0}}}


def plate_fig5() -> tuple[list, dict]:
    data = pd.read_csv(DERIVED / "fig5_relative_influence.csv", encoding="utf-8")
    order = [("Core", "Core"), ("Core", "Periphery"),
             ("Periphery", "Core"), ("Periphery", "Periphery")]

    def notes(r, n):
        return [
            {"x": 0.04, "y": 0.95, "text": _r_text(r, n), "ha": "left", "va": "top"},
            {"x": 0.62, "y": 0.72, "text": "Greater\ndiscursive\ninfluence"},
            {"x": 0.62, "y": 0.22, "text": "Greater\nattributational\ninfluence"},
        ]

    panels = _pane_panels(data, order, ylabel="Relative influence\n(z-scores)", xlabel="Year",
                          fit="loess", band="fit", reference=0.0, connect=False,
                          notes_for=notes, palette=["#1f1f1f"], fit_color="#0072b2",
                          xticks=[1990, 1995, 2000, 2005, 2010])
    computed = {}
    for sender, receiver in order:
        part = data[(data["sender_cp"] == sender) & (data["receiver_cp"] == receiver)]
        computed[f"{sender}→{receiver}"] = round(_pearson(part["Year"], part["mean"]), 3)
    return panels, {"computed": computed,
                    "layout": {"columns": 2.0, "height_mm": 168.0,
                               "sharex": True, "sharey": True, "letters": False,
                               "margins": {"bottom": 13.0}}}


def plate_fig3() -> tuple[list, dict]:
    gini = pd.read_csv(DERIVED / "fig3_gini.csv", encoding="utf-8")
    central = pd.read_csv(DERIVED / "fig3_centrality.csv", encoding="utf-8")
    panels = []
    computed = {"gini": {}, "centrality": {}}
    for network in ("Attributional", "Discursive"):
        part = gini[gini["network"] == network].sort_values("Year")
        r = _pearson(part["Year"], part["gini"])
        computed["gini"][network] = round(r, 3)
        panels.append(grammar.panel(
            "trend_with_uncertainty", part, x="Year", y="gini", fit="poly3",
            title=f"{network} influence", ylabel="Gini coefficient",
            xlabel="Year", legend=False, palette=["#1f1f1f"], fit_color="#0072b2",
            notes=[{"x": 0.04, "y": 0.95, "text": f"r = {r:.2f}, n = {len(part)}",
                    "ha": "left", "va": "top"}]))
    for network in ("Attributional", "Discursive"):
        part = central[central["network"] == network].copy().sort_values("Year")
        part["series"] = part["cp"]
        part["lo"] = part["mean"] - part["se"]
        part["hi"] = part["mean"] + part["se"]
        rs, ns = {}, {}
        for cp, sub in part.groupby("series"):
            rs[cp] = _pearson(sub["Year"], sub["mean"])
            ns[cp] = len(sub)
        computed["centrality"][network] = {k: round(v, 3) for k, v in rs.items()}
        panels.append(grammar.panel(
            "trend_with_uncertainty", part, x="Year", y="mean", lo="lo", hi="hi",
            series="series", band="data", fit="lm", reference=0.0,
            xlabel="Year" if network == "Attributional" else "",
            ylabel="Country centrality\n(z-scores)" if network == "Attributional" else "",
            title=f"{network} influence", legend=network == "Attributional",
            palette=["#3b4cc0", "#d62728"], data_band_color="#b3b3b3",
            legend_below=True, legend_cols=2,
            annotate={"Core": (f"r = {rs['Core']:.2f}, n = {ns['Core']}", 0.04, 0.93),
                      "Periphery": (f"r = {rs['Periphery']:.2f}, n = {ns['Periphery']}",
                                    0.04, 0.79)}))
    return panels, {"computed": computed,
                    "layout": {"columns": 2.0, "height_mm": 168.0, "letters": True,
                               "margins": {"bottom": 24.0}}}


def plate_fig1() -> tuple[list, dict]:
    counts = pd.read_csv(DERIVED / "fig1a_country_share.csv", encoding="utf-8")
    per_term = pd.read_csv(DERIVED / "fig1b_term_counts.csv", encoding="utf-8")
    r = _pearson(np.log10(per_term["n_papers"]), np.log10(per_term["n_cites"]))
    panels = [
        grammar.panel("ranked_composition", counts, label="name", value="percent",
                      top=20, percent=True, value_fmt="{:.0f}",
                      xtick_rotation=45, ylabel="Per cent of term papers", xlabel="",
                      bar_color="#4d4d4d"),
        grammar.panel("density_relationship", per_term, x="n_papers", y="n_cites",
                      xlabel="Number of term papers per term",
                      ylabel="Number of attributional papers per term",
                      marginals="top", colorbar=True, cbar_label="",
                      letter_dy_pt=34.0),
    ]
    return panels, {"computed": {"hexbin_r": round(r, 3)},
                    "layout": {"columns": 2.0, "height_mm": 96.0, "letters": True,
                               "width_ratios": [1.0, 1.35],
                               "margins": {"top": 17.0, "bottom": 15.0}}}


# --------------------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------------------

def _render(name: str, panels: list, layout_kw: dict) -> dict:
    stem = OUT / name
    fig = grammar.plate(panels, **layout_kw)
    report = getattr(fig, "_figpipe_report", composite.inspect(fig))
    problems = composite.check(fig, report)
    paths = layout.save(fig, stem)
    # The span-bbox overlap test is run at GLYPH level: rotated tick labels (the 20 rotated
    # country names of Fig 1a) make the span boxes overlap while the glyphs are clean, and a
    # check that cries wolf on every rotated axis is a check everyone learns to ignore.
    a = audit.audit(paths[0], expect_width_mm=WIDTH_MM, check_overlap=False)
    collisions = audit.overlapping_glyphs(paths[0])
    hard = [f for f in a["findings"]
            if f["check"] in ("font_size", "width", "height", "font_type", "exists")]
    if collisions:
        hard.append({"check": "text_collision",
                     "detail": f"{len(collisions)} span pair(s) printed on top of each other",
                     "examples": collisions[:5]})
    return {"figure": name,
            "pdf": str(pathlib.Path(paths[0]).relative_to(ROOT)),
            "png": str(pathlib.Path(paths[1]).relative_to(ROOT)),
            "n_panels": report["n_panels"],
            "letters": [lt["letter"] for lt in report.get("letters", [])],
            "gaps_x_mm": report["gaps_x_mm"], "gaps_y_mm": report["gaps_y_mm"],
            "width_mm": a["width_mm"], "height_mm": a["height_mm"],
            "audit_ok": a["ok"], "audit_hard_findings": hard,
            "text_collisions": collisions,
            "geometry_problems": problems}


def _delta(computed: dict, published: dict) -> dict:
    out = {}
    for k, v in published.items():
        got = computed.get(k)
        if isinstance(v, dict):
            out[k] = _delta(got or {}, v)
        else:
            out[k] = {"computed": got, "published": v,
                      "delta": None if got is None else round(got - v, 3)}
    return out


def render() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    builders = [("fig1_term_papers_and_density", plate_fig1, PUBLISHED["fig1b_r"]),
                ("fig3_centrality_and_gini", plate_fig3, None),
                ("fig5_relative_influence", plate_fig5, None),
                ("fig7_national_signature_mimicry", plate_fig7, None)]
    figures = []
    for name, builder, _ in builders:
        panels, meta = builder()
        rep = _render(name, panels, meta["layout"])
        rep["computed"] = meta["computed"]
        rep.update(FIGURE_META.get(name, {}))
        figures.append(rep)
        print(f"  {name:<34} {rep['n_panels']} panels  {rep['width_mm']:.1f} x "
              f"{rep['height_mm']:.1f} mm  audit={'OK' if rep['audit_ok'] else 'FAIL'}  "
              f"geometry={'OK' if not rep['geometry_problems'] else 'PROBLEM'}  "
              f"collisions={len(rep['text_collisions'])}")
        for f in rep["audit_hard_findings"]:
            print(f"      {f['check']}: {f['detail'][:100]}")
        for p in rep["geometry_problems"]:
            print(f"      geometry: {p[:120]}")
        for c in rep["text_collisions"]:
            print(f"      collision: {c['a'][:26]!r} <-> {c['b'][:26]!r} "
                  f"({c['glyph_pairs']} glyph pairs)")
    fig1 = next(f for f in figures if f["figure"].startswith("fig1"))
    fig3 = next(f for f in figures if f["figure"].startswith("fig3"))
    fig5 = next(f for f in figures if f["figure"].startswith("fig5"))
    fig7 = next(f for f in figures if f["figure"].startswith("fig7"))
    checks = {
        "fig1b_r": _delta({"r": fig1["computed"]["hexbin_r"]}, {"r": PUBLISHED["fig1b_r"]})["r"],
        "fig3": {"gini": _delta(fig3["computed"]["gini"], PUBLISHED["fig3_gini_r"]),
                 "centrality": _delta(fig3["computed"]["centrality"],
                                      PUBLISHED["fig3_centrality_r"])},
        "fig5": _delta(fig5["computed"], PUBLISHED["fig5_r"]),
        "fig7": _delta(fig7["computed"], PUBLISHED["fig7_r"]),
    }
    report = {
        "about": ("Reproduction of the seed paper's figures (NHB 2026, national influence) "
                  "from its own published data, through figpipe.grammar intents."),
        "reproduction_layers": REPRODUCTION_LAYERS,
        "not_reproduced": {
            "Fig 2": {"layer": "L0/L1", "why": "QAP regression coefficients and permutation "
                                               "outputs are not in the published data package"},
            "Fig 4": {"layer": "L1/L2", "why": "same construction as Fig 3 from relative "
                                               "influence; omitted to keep the run short -- the "
                                               "derived tables already support it"},
            "Fig 6": {"layer": "L2", "why": "arc diagram and region matrix need a country->region "
                                            "mapping the seed does not include (the R recipe uses "
                                            "raster::ccodes + a custom UNREGION1 table)"},
        },
        "discrepancies": DISCREPANCIES,
        "agreement": checks,
        "figures": figures,
    }
    # THE REPORT CHECKS ITSELF. Counting statistics by hand produced a wrong number once
    # ("14 of 14" when there were 15), so the count and the worst delta are computed here and
    # asserted against the data, not written down from memory.
    deltas = []

    def walk(node):
        if isinstance(node, dict):
            if "published" in node and "computed" in node:
                if node.get("delta") is not None:
                    deltas.append(node["delta"])
                return
            for v in node.values():
                walk(v)

    walk(checks)
    worst = max((abs(d) for d in deltas), default=None)
    report["self_check"] = {
        "statistics_recorded": len(deltas),
        "worst_abs_delta": worst,
        "threshold": 0.01,
        "ok": worst is not None and worst <= 0.01,
        "hard_findings": sum(len(f["audit_hard_findings"]) for f in figures),
        "text_collisions": sum(len(f["text_collisions"]) for f in figures),
        "note": "counts are derived from the agreement tree, never typed by hand",
    }
    (OUT / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n  computed vs published:")
    print(f"    Fig1b r            {checks['fig1b_r']['computed']:+.3f} vs "
          f"{checks['fig1b_r']['published']:+.2f}")
    for net, v in checks["fig3"]["gini"].items():
        print(f"    Fig3 gini {net:<14} {v['computed']:+.3f} vs {v['published']:+.2f}")
    for net, d in checks["fig3"]["centrality"].items():
        for cp, v in d.items():
            print(f"    Fig3 cent {net:<14} {cp:<10} {v['computed']:+.3f} vs "
                  f"{v['published']:+.2f}")
    for name in ("fig5", "fig7"):
        for k, v in checks[name].items():
            print(f"    {name.upper()} {k:<20} {v['computed']:+.3f} vs {v['published']:+.2f}")
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stage", choices=["derive", "render", "all"], default="all")
    ap.add_argument("--refresh", action="store_true",
                    help="recompute the edgelist aggregation instead of using the cache")
    args = ap.parse_args(argv)
    if args.stage in ("derive", "all"):
        print("  deriving panel datasets from the seed's raw data ...")
        derive(refresh=args.refresh)
    if args.stage in ("render", "all"):
        if not (DERIVED / "fig7_mimicry.csv").is_file():
            print("  derived data missing; run --stage derive first")
            return 1
        print("  rendering reproductions ...")
        render()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
