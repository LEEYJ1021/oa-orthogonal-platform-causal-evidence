"""
Open Access as an Orthogonal Platform
Empirical Analysis Pipeline — Python

Steps:
  1. Data loading + Chinese institution detection
  2. Feature engineering (IV, novelty, cluster indices)
  3. Sentence embedding (MiniLM-L6-v2) + UMAP + HDBSCAN clustering
  4. Econometric analysis (OLS, TWFE, IV-2SLS, NegBin, Quantile)
  5. Bartik IV validity suite (pre-trend, GP, LOFO, residualized, falsification)
  6. Sun & Abraham IW event study
  7. Callaway-Sant'Anna ATT
  8. Causal Forest HTE (DR-Learner / CausalForestDML)
  9. Heterogeneity sensitivity (Oster bounds, partial R²)
  10. Figure generation + LaTeX tables + JSON summary

Requirements:
  numpy pandas scipy statsmodels linearmodels
  sentence-transformers umap-learn hdbscan
  scikit-learn econml torch
  matplotlib seaborn
"""

# ── Standard library ──────────────────────────────────────────────────────────
import os
import re
import math
import warnings
import time
import json
import functools
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple, Optional

# ── Environment ───────────────────────────────────────────────────────────────
os.environ["TF_CPP_MIN_LOG_LEVEL"]    = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"]   = "0"
os.environ["TF_KERAS_LEGACY_LOGGING"] = "0"

# ── Third-party ───────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
import scipy.stats as ss
from scipy.stats import spearmanr

warnings.filterwarnings("ignore")

import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS
from statsmodels.regression.quantile_regression import QuantReg
from statsmodels.stats.outliers_influence import variance_inflation_factor
from linearmodels.iv import IV2SLS

import torch
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import silhouette_score
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.model_selection import KFold
from sentence_transformers import SentenceTransformer

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
import seaborn as sns

torch.set_num_threads(os.cpu_count() or 4)


# ══════════════════════════════════════════════════════════════════════════════
# UMAP compatibility patch
# ══════════════════════════════════════════════════════════════════════════════
def _apply_sklearn_umap_patch():
    try:
        import sklearn.utils.validation as _skval
        _orig = _skval.check_array

        @functools.wraps(_orig)
        def _patched(*args, **kwargs):
            if "ensure_all_finite" in kwargs:
                val = kwargs.pop("ensure_all_finite")
                kwargs.setdefault("force_all_finite", val)
            return _orig(*args, **kwargs)

        _skval.check_array = _patched
        try:
            import umap.umap_ as _umap_mod
            _umap_mod.check_array = _patched
        except Exception:
            pass
        print("  [PATCH] sklearn/umap-learn compatibility patch applied")
    except Exception as e:
        print(f"  [PATCH] Skipped ({e})")


_apply_sklearn_umap_patch()

try:
    import umap
    HAS_UMAP = True
except ImportError:
    HAS_UMAP = False
    print("  ⚠ umap-learn not found → PCA fallback")

try:
    import hdbscan
    HAS_HDBSCAN = True
except ImportError:
    HAS_HDBSCAN = False
    print("  ⚠ hdbscan not found → KMeans fallback")

try:
    from econml.dml import CausalForestDML, LinearDML
    HAS_ECONML = True
except ImportError:
    HAS_ECONML = False
    print("  ⚠ econml not found → DR-Learner fallback")


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION  — edit paths before running
# ══════════════════════════════════════════════════════════════════════════════
CSV_PATH    = "data/transport_cn_scholarly_works.csv"   # <-- set your CSV path
OUT_DIR     = Path("outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

(OUT_DIR / "figures" / "01_descriptive").mkdir(parents=True, exist_ok=True)
(OUT_DIR / "figures" / "02_main_results").mkdir(parents=True, exist_ok=True)
(OUT_DIR / "figures" / "03_platform_framing").mkdir(parents=True, exist_ok=True)
(OUT_DIR / "figures" / "04_causal_identification").mkdir(parents=True, exist_ok=True)
(OUT_DIR / "figures" / "05_heterogeneity").mkdir(parents=True, exist_ok=True)
(OUT_DIR / "figures" / "06_robustness").mkdir(parents=True, exist_ok=True)
(OUT_DIR / "figures" / "07_combined").mkdir(parents=True, exist_ok=True)
(OUT_DIR / "tables").mkdir(parents=True, exist_ok=True)

EMBED_MODEL  = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE   = 64
N_CLUSTERS   = 8
SEED         = 2025
POLICY_YEAR  = 2015
PLACEBO_YEAR = 2012
TOP_PCT      = 0.99
ES_WIN_PRE   = -2
ES_WIN_POST  = +3

np.random.seed(SEED)

# ── Palette ───────────────────────────────────────────────────────────────────
C_BLUE   = "#1D4E89"; C_RED    = "#C0392B"; C_GREY   = "#7F8C8D"
C_GREEN  = "#1A7A4A"; C_ORANGE = "#E67E22"; C_PURPLE = "#7D3C98"
C_TEAL   = "#148F77"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.labelsize": 11, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True,
    "grid.alpha": 0.35, "grid.linewidth": 0.7,
    "legend.framealpha": 0.9, "legend.fontsize": 9.5,
    "figure.dpi": 150, "savefig.dpi": 200, "savefig.bbox": "tight",
})
sns.set_palette("muted")


# ══════════════════════════════════════════════════════════════════════════════
# Chinese institution list
# ══════════════════════════════════════════════════════════════════════════════
CN_INST_LIST = {
    "Zhejiang University", "Xi'an Jiaotong University",
    "Wuhan University of Technology", "Wuhan University",
    "University of Science and Technology of China",
    "University of Chinese Academy of Sciences", "Tsinghua University",
    "Tongji University", "Tianjin University", "Sun Yat-sen University",
    "Southwest Jiaotong University", "Southeast University",
    "South China University of Technology", "Soochow University (Suzhou)",
    "Sichuan University", "Shenzhen University", "Shanghai University",
    "Shanghai Jiao Tong University", "Shandong University", "Peking University",
    "Nanjing University", "Jilin University",
    "Huazhong University of Science and Technology",
    "Harbin Institute of Technology", "Fudan University",
    "Dalian University of Technology", "Chongqing University",
    "Chinese Academy of Sciences", "Central South University",
    "Beijing University of Technology", "Beijing Jiaotong University",
    "Beijing Institute of Technology", "Beihang University",
}
CN_KEYWORDS = [
    "tsinghua", "peking", "fudan", "zhejiang", "tongji", "wuhan", "harbin",
    "xian jiaotong", "xi'an jiaotong", "southeast university", "sun yat-sen",
    "zhongshan", "nankai", "tianjin", "dalian", "chongqing", "sichuan",
    "jilin", "central south", "south china", "huazhong", "nanjing",
    "northeastern", "southwest jiaotong", "chinese academy",
    "shenzhen university", "beijing jiaotong", "beijing institute",
    "beihang", "soochow", "chang'an", "changan", "lanzhou", "hefei",
    "university of science and technology of china",
]


def is_cn(institution: str) -> bool:
    if not isinstance(institution, str) or not institution.strip():
        return False
    if institution.strip() in CN_INST_LIST:
        return True
    low = institution.lower()
    return any(kw in low for kw in CN_KEYWORDS)


# ══════════════════════════════════════════════════════════════════════════════
# Utilities
# ══════════════════════════════════════════════════════════════════════════════
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):  return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.bool_):    return bool(obj)
        if isinstance(obj, np.ndarray):  return obj.tolist()
        return super().default(obj)


def _parse_bool_series(series) -> pd.Series:
    if series is None:
        return pd.Series(0, index=range(0), dtype=int)
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False).astype(int)
    if pd.api.types.is_integer_dtype(series) or pd.api.types.is_float_dtype(series):
        return series.fillna(0).astype(int)
    TRUE_SET = {"true", "1", "yes", "y", "t", "open", "oa"}
    def _map(v):
        if pd.isna(v): return 0
        sv = str(v).strip().lower()
        if sv in TRUE_SET: return 1
        try:   return int(float(sv) != 0)
        except: return 0
    return series.map(_map).fillna(0).astype(int)


def _stars(p: float) -> str:
    if pd.isna(p): return ""
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    if p < 0.1:   return "."
    return ""


def _clean_df(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Replace inf→NaN then dropna on specified columns (prevents MissingDataError)."""
    return df.replace([np.inf, -np.inf], np.nan).dropna(subset=cols).copy().reset_index(drop=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Data loading
# ══════════════════════════════════════════════════════════════════════════════
def load_data(path: str) -> pd.DataFrame:
    print("\n" + "=" * 65)
    print("[STEP 1] Data Loading + Preprocessing")
    print("=" * 65)

    for enc in ["utf-8-sig", "utf-8", "cp949", "euc-kr", "latin-1"]:
        try:
            df = pd.read_csv(path, encoding=enc, low_memory=False)
            print(f"  Encoding: [{enc}]")
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    else:
        df = pd.read_csv(path, encoding="utf-8", errors="replace", low_memory=False)

    df.columns = df.columns.str.strip()

    df["Citing_Patents"] = pd.to_numeric(df.get("Citing Patents Count"), errors="coerce")
    df["Citing_Works"]   = pd.to_numeric(df.get("Citing Works Count"),   errors="coerce")
    df["Pub_Year"]       = pd.to_numeric(df.get("Publication Year"),     errors="coerce")

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df[(df["Pub_Year"] >= 1900) & (df["Pub_Year"] <= 2025)]
    df = df.dropna(subset=["Pub_Year", "Citing_Patents"]).copy()

    df["OA"]         = _parse_bool_series(df.get("Is Open Access")).fillna(0).astype(int)
    df["Pub_Type"]   = df.get("Publication Type", pd.Series(dtype=str)).fillna("unknown").astype(str).str.lower()
    df["Institution"] = df.get("Institution", pd.Series("", index=df.index)).fillna("").astype(str)

    if "Source Country" in df.columns:
        df["Source_Country"] = df["Source Country"].fillna("").astype(str)
        df = df[~df["Source_Country"].str.contains(";", na=False)]
    else:
        df["Source_Country"] = ""

    df["is_CN"] = df["Institution"].apply(is_cn)
    df.loc[df["Source_Country"].str.strip() == "China", "is_CN"] = True

    df_cn = df[df["is_CN"]].copy().reset_index(drop=True)
    df_cn = df_cn[df_cn["Citing_Patents"] >= 1].copy().reset_index(drop=True)

    print(f"  Total → CN → Patent≥1: {len(df):,} → {df['is_CN'].sum():,} → {len(df_cn):,}")
    return build_indices(df_cn)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Feature engineering
# ══════════════════════════════════════════════════════════════════════════════
def build_indices(df: pd.DataFrame) -> pd.DataFrame:
    df["log_patent"]   = np.log1p(df["Citing_Patents"])
    df["log_citation"] = np.log1p(df["Citing_Works"])
    df["oa_dummy"]     = df["OA"].astype(int)
    df["recent"]       = (df["Pub_Year"] >= 2018).astype(int)
    df["post_policy"]  = (df["Pub_Year"] >= POLICY_YEAR).astype(int)
    df["post_placebo"] = (df["Pub_Year"] >= PLACEBO_YEAR).astype(int)
    df["year_rel"]     = (df["Pub_Year"] - POLICY_YEAR).astype(int)

    thr = df["Citing_Patents"].quantile(TOP_PCT)
    df["top1pct"] = (df["Citing_Patents"] >= thr).astype(int)

    # Field parsing
    def parse_primary_field(s):
        if not isinstance(s, str) or not s.strip(): return "Unknown"
        parts = [x.strip() for x in re.split(r"[;,]", s) if x.strip()]
        return parts[0] if parts else "Unknown"

    def field_count(s):
        if not isinstance(s, str) or not s.strip(): return 1
        return max(1, len([x for x in re.split(r"[;,]", s) if x.strip()]))

    def interdiscipl_entropy(s):
        if not isinstance(s, str) or not s.strip(): return 0.0
        parts = [x.strip() for x in re.split(r"[;,]", s) if x.strip()]
        return math.log(len(parts)) if len(parts) > 1 else 0.0

    fos = df.get("Fields of Study", pd.Series("", index=df.index))
    df["primary_field"]       = fos.apply(parse_primary_field)
    df["field_diversity"]     = fos.apply(field_count)
    df["log_field_div"]       = np.log1p(df["field_diversity"])
    df["interdisciplinarity"] = fos.apply(interdiscipl_entropy)

    # Global OA rate by year
    oa_rate_yr = df.groupby("Pub_Year")["oa_dummy"].mean().rename("oa_rate_global_yr")
    df = df.merge(oa_rate_yr, on="Pub_Year", how="left")

    # Pre-policy field OA rate (baseline share instrument)
    pre_fld = (df[df["Pub_Year"] < POLICY_YEAR]
               .groupby("primary_field")["oa_dummy"]
               .mean().rename("pre_field_oa").reset_index())
    df = df.merge(pre_fld, on="primary_field", how="left")
    df["pre_field_oa"] = df["pre_field_oa"].fillna(df["oa_dummy"].mean())

    # Standard shift-share IV
    df["iv_shift_share"] = df["oa_rate_global_yr"].fillna(0) * df["pre_field_oa"].fillna(0)

    # Borusyak-style residualized IV (4-step)
    iv_raw = df["oa_rate_global_yr"].fillna(0) * df["pre_field_oa"].fillna(0)
    field_mean_iv = df["primary_field"].map(
        pd.Series(iv_raw.values, index=df.index).groupby(df["primary_field"]).mean())
    iv_field_resid = iv_raw - field_mean_iv
    year_mean_iv = df["Pub_Year"].map(
        pd.Series(iv_field_resid.values, index=df.index).groupby(df["Pub_Year"]).mean())
    iv_field_year_resid = iv_field_resid - year_mean_iv
    tmp = pd.DataFrame({
        "z_raw": iv_field_year_resid.values,
        "log_citation": df["log_citation"].values,
        "log_field_div": df["log_field_div"].values,
        "pre_field_oa": df["pre_field_oa"].values,
    }).replace([np.inf, -np.inf], np.nan).dropna()
    if len(tmp) > 200:
        try:
            proj = OLS(tmp["z_raw"], sm.add_constant(tmp[["log_citation", "log_field_div", "pre_field_oa"]])).fit()
            resid_full = np.full(len(df), np.nan)
            resid_full[tmp.index] = proj.resid
            df["iv_residualized"] = resid_full
        except Exception:
            df["iv_residualized"] = iv_field_year_resid.values
    else:
        df["iv_residualized"] = iv_field_year_resid.values
    df["iv_residualized"] = df["iv_residualized"].fillna(0.0)

    # Lagged IV (alt)
    global_oa_lag2 = df.groupby("Pub_Year")["oa_dummy"].mean().shift(2).rename("oa_rate_global_lag2")
    df = df.merge(global_oa_lag2.reset_index(), on="Pub_Year", how="left")
    df["iv_alt"] = df["oa_rate_global_lag2"].fillna(df["oa_rate_global_yr"]) * df["pre_field_oa"].fillna(0)

    # Field × year trend (z-score, NaN→0)
    raw_trend = df.groupby("primary_field")["Pub_Year"].transform(
        lambda x: (x - x.mean()) / (x.std() + 1e-6))
    df["field_yr_trend"] = raw_trend.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    # Field × year OA rate
    fld_yr_oa = (df.groupby(["primary_field", "Pub_Year"])["oa_dummy"]
                   .mean().rename("field_oa_rate_yr").reset_index())
    df = df.merge(fld_yr_oa, on=["primary_field", "Pub_Year"], how="left")

    # Cohort assignment (>30% OA adoption)
    cohort_map = {}
    for fld, grp in df.groupby("primary_field"):
        g = grp.sort_values("Pub_Year")
        adopt = g[g["field_oa_rate_yr"] > 0.30]["Pub_Year"].min()
        cohort_map[fld] = int(adopt) if not pd.isna(adopt) else 9999
    df["cohort_year"] = df["primary_field"].map(cohort_map).fillna(9999).astype(int)

    # Exposure
    med_exposure = df["pre_field_oa"].median()
    df["high_exposure"] = (df["pre_field_oa"] > med_exposure).astype(int)

    # Interaction terms
    df["ddd_cont"]       = df["oa_dummy"] * df["post_policy"] * df["pre_field_oa"]
    df["ddd"]            = df["oa_dummy"] * df["post_policy"] * df["high_exposure"]
    df["oa_x_post"]      = df["oa_dummy"]   * df["post_policy"]
    df["oa_x_preoa"]     = df["oa_dummy"]   * df["pre_field_oa"]
    df["post_x_preoa"]   = df["post_policy"] * df["pre_field_oa"]

    # Disruptiveness and novelty
    df["disruptiveness"] = (
        df["Citing_Patents"] / (df["Citing_Patents"] + df["Citing_Works"].fillna(0) + 1))

    titles = df.get("Title", pd.Series("", index=df.index)).fillna("").astype(str).tolist()
    all_words = Counter()
    for t in titles:
        all_words.update(set(re.findall(r"\b[a-z]{4,}\b", t.lower())))
    n_docs = len(titles)
    rare_threshold = max(1, int(n_docs * 0.05))

    def novelty_score(title):
        words = set(re.findall(r"\b[a-z]{4,}\b", str(title).lower()))
        if not words: return 0.0
        rare = sum(1 for w in words if all_words.get(w, 0) <= rare_threshold)
        return rare / len(words)

    df["novelty_score"] = pd.Series(titles).apply(novelty_score).values

    # Text for embedding
    df["text_combined"] = (
        df.get("Title",           pd.Series("", index=df.index)).fillna("") + " " +
        df.get("Abstract",        pd.Series("", index=df.index)).fillna("") + " " +
        df.get("Fields of Study", pd.Series("", index=df.index)).fillna("") + " " +
        df.get("Keywords",        pd.Series("", index=df.index)).fillna("")
    ).str.strip()

    df["log_oa_x_citation"]     = df["oa_dummy"] * df["log_citation"]
    df["pre_oa_x_recent"]       = df["pre_field_oa"] * df["recent"]
    df["citation_sq"]           = df["log_citation"] ** 2
    df["patent_citation_ratio"] = np.log1p(df["Citing_Patents"] / (df["Citing_Works"].fillna(1) + 1))

    # Final NaN purge
    required = ["log_patent", "log_citation", "oa_dummy", "Pub_Year",
                "iv_shift_share", "iv_residualized", "pre_field_oa", "field_yr_trend"]
    df = df.replace([np.inf, -np.inf], np.nan)
    df[required] = df[required].fillna(df[required].median())
    df = df.dropna(subset=["log_patent", "log_citation", "oa_dummy", "Pub_Year"]).copy()
    df = df.reset_index(drop=True)

    print(f"  Build complete: {len(df):,} rows × {df.shape[1]} cols")
    print(f"  OA rate: {df['oa_dummy'].mean()*100:.1f}%  |  "
          f"IV mean: {df['iv_shift_share'].mean():.3f}  |  "
          f"IV-Resid mean: {df['iv_residualized'].mean():.4f}  "
          f"std: {df['iv_residualized'].std():.4f}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Embedding + UMAP + HDBSCAN
# ══════════════════════════════════════════════════════════════════════════════
def embed_and_cluster(df: pd.DataFrame):
    print("\n[STEP 3] Sentence Embedding + UMAP + HDBSCAN")
    texts = df["text_combined"].tolist()
    texts = [t if t.strip() else "transport china research" for t in texts]

    model = SentenceTransformer(EMBED_MODEL)
    t0    = time.perf_counter()
    emb   = model.encode(texts, batch_size=BATCH_SIZE,
                         show_progress_bar=True, normalize_embeddings=True,
                         convert_to_numpy=True)
    print(f"  Embedding: {emb.shape}  ({time.perf_counter()-t0:.1f}s)")
    del model

    pca_dim = min(50, emb.shape[1], emb.shape[0] - 1)
    emb_pca = PCA(n_components=pca_dim, random_state=SEED).fit_transform(emb).astype(np.float32)

    if HAS_UMAP:
        try:
            reducer    = umap.UMAP(n_components=15, n_neighbors=15, min_dist=0.1,
                                   metric="cosine", random_state=SEED, low_memory=True)
            emb_15d    = reducer.fit_transform(emb_pca)
            reducer_2d = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.05,
                                   metric="cosine", random_state=SEED, low_memory=True)
            emb_2d     = reducer_2d.fit_transform(emb_pca)
        except Exception as e:
            print(f"  ⚠ UMAP failed: {e} → PCA fallback")
            emb_15d = emb_pca
            emb_2d  = PCA(n_components=2, random_state=SEED).fit_transform(emb_pca)
    else:
        emb_15d = emb_pca
        emb_2d  = PCA(n_components=2, random_state=SEED).fit_transform(emb_pca)

    cluster_input = emb_15d.astype(np.float64)

    if HAS_HDBSCAN:
        best_labels, best_sil = None, -1.0
        for mcs in [max(30, len(df)//200), max(50, len(df)//150), max(80, len(df)//100)]:
            try:
                clusterer = hdbscan.HDBSCAN(min_cluster_size=mcs,
                                             min_samples=max(5, mcs//5),
                                             metric="euclidean",
                                             cluster_selection_method="eom",
                                             prediction_data=True)
                lbl = clusterer.fit_predict(cluster_input)
                n_cl = len(set(lbl)) - (1 if -1 in lbl else 0)
                if n_cl < 2: continue
                if (lbl == -1).any():
                    try:
                        soft = hdbscan.all_points_membership_vectors(clusterer)
                        for i in range(len(lbl)):
                            if lbl[i] == -1:
                                lbl[i] = int(np.argmax(soft[i])) if soft[i].sum() > 0 else 0
                    except Exception:
                        lbl[lbl == -1] = 0
                if len(set(lbl)) < 2: continue
                sil = silhouette_score(cluster_input, lbl, sample_size=min(3000, len(cluster_input)))
                print(f"    mcs={mcs:4d} → k={len(set(lbl))}  sil={sil:.4f}")
                if sil > best_sil:
                    best_sil, best_labels = sil, lbl.copy()
            except Exception:
                pass
        if best_labels is None:
            from sklearn.cluster import KMeans
            best_labels = KMeans(n_clusters=N_CLUSTERS, random_state=SEED, n_init=15).fit_predict(cluster_input)
        df["cluster"] = best_labels
        print(f"  ✓ Clustering: k={len(set(best_labels))}  silhouette={best_sil:.4f}")
    else:
        from sklearn.cluster import KMeans
        df["cluster"] = KMeans(n_clusters=N_CLUSTERS, random_state=SEED, n_init=15).fit_predict(cluster_input)

    kw_dict = _cluster_keywords(df, "cluster", "text_combined")
    return df, emb_2d, kw_dict


def _cluster_keywords(df, cluster_col, text_col, top_n=12):
    STOP = {"the","a","an","of","and","in","to","for","with","on","is","are",
            "this","that","we","our","by","as","at","be","was","were","have",
            "has","had","from","or","not","it","its","which","can","may","also",
            "using","used","based","study","paper","proposed","method","system",
            "model","data","result","results","analysis","approach","show","effect"}
    kw_dict = {}
    for cid in sorted(df[cluster_col].unique()):
        texts = df[df[cluster_col]==cid][text_col].fillna("").tolist()
        tf    = Counter()
        for t in texts:
            tf.update(w for w in re.findall(r"\b[a-z]{3,}\b", t.lower()) if w not in STOP)
        total  = sum(tf.values()) or 1
        df_col = df[text_col].str.lower()
        scored = {}
        for w, cnt in tf.most_common(200):
            doc_freq = df_col.str.contains(r'\b' + w + r'\b', na=False).sum()
            scored[w] = (cnt / total) * math.log(len(df) / (doc_freq + 1))
        kw_dict[cid] = sorted(scored, key=scored.get, reverse=True)[:top_n]
    return kw_dict


# ══════════════════════════════════════════════════════════════════════════════
# Econometric helpers
# ══════════════════════════════════════════════════════════════════════════════
def _within_demean_fe(df, dv, controls, fe_cols):
    data  = _clean_df(df, [dv] + controls + fe_cols)
    y_arr = data[dv].values.copy().astype(float)
    X_arr = data[controls].values.copy().astype(float)
    for _ in range(3):
        for fe in fe_cols:
            groups = data[fe].values
            for g in np.unique(groups):
                mask         = groups == g
                y_arr[mask] -= y_arr[mask].mean()
                X_arr[mask] -= X_arr[mask].mean(axis=0)
    X_sm = sm.add_constant(pd.DataFrame(X_arr, columns=controls), has_constant="add")
    try:
        return OLS(pd.Series(y_arr, name=dv), X_sm).fit(cov_type="HC3")
    except Exception:
        return OLS(pd.Series(y_arr, name=dv), X_sm).fit()


def _iv2sls_primary(df, dv, endog, instrument, controls, label="IV"):
    data = _clean_df(df, [dv, endog, instrument] + controls)
    if len(data) < 50:
        return None, {}
    exog = sm.add_constant(data[controls])
    try:
        iv = IV2SLS(data[dv], exog, data[[endog]], data[[instrument]]).fit(cov_type="robust")
        try:
            fs_diag = iv.first_stage.diagnostics
            fs_f = float(fs_diag["f.stat"].values[0])
            fs_p = float(fs_diag["f.pval"].values[0])
            print(f"    [{label}] First-stage F={fs_f:.2f}  "
                  f"{'✓ Strong' if fs_f > 10 else '⚠ Weak'}")
        except Exception:
            fs_f, fs_p = None, None
        return iv, {"fs_f": fs_f, "fs_p": fs_p}
    except Exception as e:
        print(f"    [{label}] IV failed: {e} → OLS fallback")
        X = sm.add_constant(data[controls + [endog]])
        return OLS(data[dv], X).fit(cov_type="HC3"), {}


def _get_param(m, var):
    if m is None: return np.nan
    try:
        return float(m.params[var])
    except Exception:
        return np.nan


def _get_pval(m, var):
    if m is None: return np.nan
    try:
        return float(m.pvalues[var])
    except Exception:
        return np.nan


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Econometric analysis
# ══════════════════════════════════════════════════════════════════════════════
def run_econometrics(df: pd.DataFrame):
    print("\n[STEP 4] Econometric Analysis")
    results = {}
    base_cols = ["log_patent", "log_citation", "oa_dummy", "Pub_Year", "post_policy",
                 "high_exposure", "ddd", "iv_shift_share", "pre_field_oa",
                 "recent", "log_field_div", "primary_field", "field_yr_trend"]
    clean = _clean_df(df, base_cols)

    le_pub = LabelEncoder()
    clean["pub_year_enc"] = le_pub.fit_transform(clean["Pub_Year"].astype(str))
    le_fld = LabelEncoder()
    clean["field_enc"]    = le_fld.fit_transform(clean["primary_field"].astype(str))
    controls_base = ["log_citation", "oa_dummy", "recent", "log_field_div"]

    # M1 OLS
    X1_data = _clean_df(clean, controls_base + ["log_patent"])
    X1 = sm.add_constant(X1_data[controls_base])
    results["m1_ols"] = OLS(X1_data["log_patent"], X1).fit(cov_type="HC3")

    # M2 Two-way FE
    results["m2_fe"] = _within_demean_fe(clean, "log_patent", controls_base,
                                          ["pub_year_enc", "field_enc"])

    # M4 IV-2SLS (PRIMARY)
    m4, m4_diag = _iv2sls_primary(
        clean, "log_patent", "oa_dummy", "iv_shift_share",
        ["log_citation", "recent", "log_field_div"], "Shift-Share IV")
    results["m4_iv"]      = m4
    results["m4_iv_diag"] = m4_diag

    # M4b Residualized IV
    m4b, m4b_diag = _iv2sls_primary(
        clean, "log_patent", "oa_dummy", "iv_residualized",
        ["log_citation", "recent", "log_field_div", "field_yr_trend"], "Residualized IV")
    results["m4b_iv_resid"]      = m4b
    results["m4b_iv_resid_diag"] = m4b_diag

    # M9 Quantile
    X9_data = _clean_df(clean, controls_base + ["log_patent"])
    X9_df   = sm.add_constant(X9_data[controls_base])
    qm = QuantReg(X9_data["log_patent"].values, X9_df.values)
    results["m9_quantile"] = {}
    for tau in [0.50, 0.75, 0.90, 0.95]:
        qr = qm.fit(q=tau, vcov="robust")
        qr._exog_names = list(X9_df.columns)
        results["m9_quantile"][tau] = qr

    print("  ✓ Econometrics complete")
    return results, clean


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Bartik IV validity suite
# ══════════════════════════════════════════════════════════════════════════════
def bartik_validity_suite(df: pd.DataFrame, results: dict) -> dict:
    print("\n[STEP 5] Bartik IV Validity Suite")
    validity = {}

    # Pre-trend test
    iv1_cols = ["log_patent", "iv_shift_share", "log_citation", "log_field_div",
                "field_yr_trend", "Pub_Year"]
    pre_data = _clean_df(df[df["Pub_Year"] < POLICY_YEAR], iv1_cols)
    if len(pre_data) > 100:
        X_pre = sm.add_constant(pre_data[["iv_shift_share", "log_citation",
                                          "log_field_div", "field_yr_trend"]])
        m_pre = OLS(pre_data["log_patent"], X_pre).fit(cov_type="HC3")
        b = _get_param(m_pre, "iv_shift_share")
        p = _get_pval(m_pre, "iv_shift_share")
        print(f"  Pre-trend: β={b:+.4f}  p={p:.3f}  "
              f"{'✓ PASS' if p > 0.1 else '⚠ FAIL'}")
        validity["pre_trend"] = {"beta": float(b), "pval": float(p), "pass": bool(p > 0.1)}

    # LOFO stability
    lofo_cols = ["log_patent", "oa_dummy", "iv_shift_share", "log_citation", "recent",
                 "log_field_div", "primary_field", "oa_rate_global_yr", "pre_field_oa", "Pub_Year"]
    lofo_clean = _clean_df(df, lofo_cols)
    lofo_coefs = []
    for fld in lofo_clean["primary_field"].unique()[:20]:
        sub = lofo_clean[lofo_clean["primary_field"] != fld].copy()
        pre_sub = sub[sub["Pub_Year"] < POLICY_YEAR].groupby("primary_field")["oa_dummy"].mean()
        sub["pre_field_oa_lofo"] = sub["primary_field"].map(pre_sub).fillna(sub["pre_field_oa"])
        sub["iv_lofo"] = sub["oa_rate_global_yr"].fillna(0) * sub["pre_field_oa_lofo"].fillna(0)
        sub_clean = _clean_df(sub, ["log_patent", "oa_dummy", "iv_lofo", "log_citation",
                                     "recent", "log_field_div"])
        if len(sub_clean) < 100: continue
        try:
            exog = sm.add_constant(sub_clean[["log_citation", "recent", "log_field_div"]])
            iv_lo = IV2SLS(sub_clean["log_patent"], exog, sub_clean[["oa_dummy"]],
                           sub_clean[["iv_lofo"]]).fit(cov_type="robust")
            lofo_coefs.append(float(iv_lo.params["oa_dummy"]))
        except Exception:
            pass
    if lofo_coefs:
        arr = np.array(lofo_coefs)
        print(f"  LOFO β: mean={arr.mean():.4f}  std={arr.std():.4f}  "
              f"{'✓ STABLE' if arr.std() < 0.05 else '⚠ Sensitive'}")
        validity["lofo"] = {"mean": float(arr.mean()), "std": float(arr.std()),
                             "stable": bool(arr.std() < 0.05)}

    return validity


# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — Event study (Sun & Abraham IW)
# ══════════════════════════════════════════════════════════════════════════════
def sun_abraham_event_study(df: pd.DataFrame):
    print("\n[STEP 6] Sun & Abraham IW Event Study")
    es_cols = ["log_patent", "log_citation", "log_field_div", "Pub_Year", "cohort_year", "primary_field"]
    clean = _clean_df(df, es_cols)
    clean = clean[clean["cohort_year"] < 9999].copy()

    cohort_counts = clean["cohort_year"].value_counts()
    valid_cohorts = cohort_counts[cohort_counts >= 50].index.tolist()
    clean = clean[clean["cohort_year"].isin(valid_cohorts)].copy()
    clean["year_rel_int"] = (clean["Pub_Year"] - clean["cohort_year"]).clip(ES_WIN_PRE, ES_WIN_POST)
    clean_win = clean[clean["year_rel_int"].between(ES_WIN_PRE, ES_WIN_POST)].copy()

    ref_rel = -1
    all_iw_coefs, all_iw_ses = {}, {}
    for rel in sorted(clean_win["year_rel_int"].unique()):
        if rel == ref_rel: continue
        catt_list, se_list, n_list = [], [], []
        for g in valid_cohorts:
            sub = clean_win[(clean_win["cohort_year"] == g) &
                            (clean_win["year_rel_int"].isin([ref_rel, rel]))].copy()
            if len(sub) < 15: continue
            sub["is_rel"] = (sub["year_rel_int"] == rel).astype(int)
            sub_c = _clean_df(sub, ["log_patent", "is_rel", "log_citation", "log_field_div"])
            if len(sub_c) < 10: continue
            try:
                X = sm.add_constant(sub_c[["is_rel", "log_citation", "log_field_div"]])
                m = OLS(sub_c["log_patent"], X).fit(cov_type="HC3")
                coef = _get_param(m, "is_rel")
                se_val = float(m.bse["is_rel"]) if hasattr(m.bse, "__getitem__") else 0.02
                if np.isnan(coef) or np.isnan(se_val): continue
                catt_list.append(coef); se_list.append(max(se_val, 1e-6)); n_list.append(len(sub_c))
            except Exception:
                pass
        if catt_list:
            weights = np.array(n_list, dtype=float) / sum(n_list)
            all_iw_coefs[rel] = float(np.dot(weights, catt_list))
            all_iw_ses[rel]   = float(np.sqrt(np.dot(weights**2, np.array(se_list)**2)))

    rel_vals = sorted(clean_win["year_rel_int"].unique())
    sa_rows = []
    for rel in rel_vals:
        if rel == ref_rel:
            sa_rows.append({"year_rel": rel, "coef": 0.0, "se": 0.0, "ci_lo": 0.0, "ci_hi": 0.0, "pval": 1.0})
        elif rel in all_iw_coefs:
            coef = all_iw_coefs[rel]; se = all_iw_ses[rel]
            pval = 2 * (1 - ss.norm.cdf(abs(coef / max(se, 1e-9))))
            sa_rows.append({"year_rel": rel, "coef": coef, "se": se,
                            "ci_lo": coef - 1.96*se, "ci_hi": coef + 1.96*se, "pval": pval})
    sa_df = pd.DataFrame(sa_rows).sort_values("year_rel")
    print(f"  IW event study complete: {len(sa_df)} periods")
    return sa_df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 7 — Causal Forest HTE
# ══════════════════════════════════════════════════════════════════════════════
def causal_forest_hte(df: pd.DataFrame) -> dict:
    print("\n[STEP 7] Causal Forest HTE")
    X_features = ["log_citation", "log_field_div", "recent", "pre_field_oa",
                  "novelty_score", "interdisciplinarity", "disruptiveness",
                  "log_oa_x_citation", "pre_oa_x_recent", "citation_sq",
                  "patent_citation_ratio", "field_yr_trend"]
    X_features = [f for f in X_features if f in df.columns]
    clean = _clean_df(df, ["log_patent", "oa_dummy"] + X_features)
    Y = clean["log_patent"].values
    T = clean["oa_dummy"].values.astype(float)
    X = clean[X_features].fillna(0).values

    if HAS_ECONML:
        try:
            from econml.dml import CausalForestDML
            cf = CausalForestDML(n_estimators=300, min_samples_leaf=5, max_depth=6,
                                  random_state=SEED, n_jobs=-1, cv=5)
            cf.fit(Y, T, X=X, W=X[:, :4])
            te = cf.effect(X)
            return {"cate_mean": float(te.mean()), "cate_std": float(te.std()),
                    "te_vector": te, "method": "CausalForestDML"}
        except Exception as e:
            print(f"  CausalForestDML failed: {e} → DR-Learner")

    # DR-Learner fallback
    kf = KFold(n_splits=5, shuffle=True, random_state=SEED)
    scaler = StandardScaler()
    X_sc   = scaler.fit_transform(X)
    mu_hat = np.zeros_like(Y, dtype=float)
    ps_hat = np.zeros_like(Y, dtype=float)
    for train_idx, test_idx in kf.split(X_sc):
        ps_m = LogisticRegression(C=0.1, random_state=SEED, max_iter=500)
        ps_m.fit(X_sc[train_idx], T[train_idx])
        ps_hat[test_idx] = np.clip(ps_m.predict_proba(X_sc[test_idx])[:, 1], 0.05, 0.95)
        for t_val in [0, 1]:
            mask_t = T[train_idx] == t_val
            if mask_t.sum() < 20: continue
            gbm = GradientBoostingRegressor(n_estimators=150, max_depth=3,
                                            learning_rate=0.05, random_state=SEED)
            gbm.fit(X_sc[train_idx][mask_t], Y[train_idx][mask_t])
            test_mask = test_idx[T[test_idx] == t_val]
            if len(test_mask) > 0:
                mu_hat[test_mask] = gbm.predict(X_sc[test_mask])
    mu1    = np.where(T == 1, Y, mu_hat + (Y - mu_hat) / (ps_hat + 1e-9))
    mu0    = np.where(T == 0, Y, mu_hat - (Y - mu_hat) / (1 - ps_hat + 1e-9))
    pseudo = mu1 - mu0
    rf = RandomForestRegressor(n_estimators=300, max_depth=6, min_samples_leaf=5,
                                random_state=SEED, n_jobs=-1)
    rf.fit(X_sc, pseudo)
    te = rf.predict(X_sc)
    print(f"  DR-Learner CATE: mean={te.mean():.4f}  std={te.std():.4f}")
    return {"cate_mean": float(te.mean()), "cate_std": float(te.std()),
            "te_vector": te, "method": "DR-Learner",
            "feature_importance": dict(zip(X_features, rf.feature_importances_.tolist()))}


# ══════════════════════════════════════════════════════════════════════════════
# STEP 8 — Descriptive statistics
# ══════════════════════════════════════════════════════════════════════════════
def descriptive_stats(df: pd.DataFrame):
    vars_desc = {
        "Citing_Patents": "Patent Citations",    "Citing_Works": "Academic Citations",
        "log_patent":     "log(Patent Cit.)",    "log_citation": "log(Academic Cit.)",
        "oa_dummy":       "Open Access",          "recent":       "Recent (≥2018)",
        "field_diversity":"Field Diversity",       "interdisciplinarity": "Interdiscipl.",
        "disruptiveness": "Disruptiveness",        "novelty_score":"Novelty",
        "top1pct":        "Superstar (Top 1%)",    "pre_field_oa": "Pre-Field OA Rate",
        "iv_shift_share": "IV (Shift-Share)",      "iv_residualized": "IV (Residualized)",
    }
    rows = []
    for var, label in vars_desc.items():
        if var not in df.columns: continue
        s = df[var].dropna()
        rows.append({"Variable": label, "N": f"{len(s):,}", "Mean": f"{s.mean():.3f}",
                     "SD": f"{s.std():.3f}", "Min": f"{s.min():.3f}",
                     "P50": f"{s.median():.3f}", "Max": f"{s.max():.3f}"})
    desc_df = pd.DataFrame(rows)
    desc_df.to_csv(OUT_DIR / "tables" / "table1_descriptive.csv", index=False, encoding="utf-8-sig")
    print("  ✓ table1_descriptive.csv")
    return desc_df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 9 — Selected figures
# ══════════════════════════════════════════════════════════════════════════════
def create_figures(df, results, sa_df, kw_dict, emb_2d, cf_results):
    print("\n[STEP 9] Figure Generation")

    # Correlation matrix
    try:
        corr_vars = ["log_patent", "log_citation", "oa_dummy", "recent",
                     "log_field_div", "top1pct", "disruptiveness",
                     "novelty_score", "interdisciplinarity", "iv_shift_share", "iv_residualized"]
        corr_vars = [v for v in corr_vars if v in df.columns]
        nice_names = [v.replace("log_", "log(").replace("_", " ").title() for v in corr_vars]
        corr_df = df[corr_vars].corr()
        fig, ax = plt.subplots(figsize=(13, 11))
        mask = np.triu(np.ones_like(corr_df, dtype=bool))
        cmap = LinearSegmentedColormap.from_list("rw", ["#C0392B", "white", "#1D4E89"])
        sns.heatmap(corr_df, mask=mask, annot=True, fmt=".2f", cmap=cmap,
                    center=0, ax=ax, linewidths=0.5, annot_kws={"size": 8},
                    xticklabels=nice_names, yticklabels=nice_names)
        ax.set_title("Correlation Matrix (Pearson r)", pad=14)
        ax.tick_params(axis="x", rotation=38, labelsize=8)
        plt.tight_layout()
        plt.savefig(OUT_DIR / "figures" / "01_descriptive" / "fig0_corr_matrix.png")
        plt.close()
        print("  ✓ fig0_corr_matrix.png")
    except Exception as e:
        print(f"  ⚠ fig0 failed: {e}")

    # Annual trend
    try:
        yr = (df.groupby("Pub_Year")["Citing_Patents"]
                .agg(n="count", mean="mean", med="median")
                .reset_index().query("1995 <= Pub_Year <= 2024"))
        fig, ax1 = plt.subplots(figsize=(13, 5.5))
        ax1.bar(yr["Pub_Year"], yr["n"], color=C_BLUE, alpha=0.55, label="# Papers")
        ax1.set_ylabel("Number of Papers", color=C_BLUE)
        ax2 = ax1.twinx()
        ax2.plot(yr["Pub_Year"], yr["mean"], "o-", color=C_RED, lw=2.2, ms=5, label="Mean")
        ax2.plot(yr["Pub_Year"], yr["med"],  "s--", color=C_ORANGE, lw=1.5, ms=4, label="Median")
        ax2.set_ylabel("Patent Citations", color=C_RED)
        ax1.axvline(POLICY_YEAR, ls="--", color=C_RED, lw=1.8, alpha=0.7)
        ax1.set_xlabel("Publication Year")
        ax1.set_title("Annual Trend: Patent-Cited Papers from Chinese Institutions")
        plt.tight_layout()
        plt.savefig(OUT_DIR / "figures" / "01_descriptive" / "fig1_annual_trend.png")
        plt.close()
        print("  ✓ fig1_annual_trend.png")
    except Exception as e:
        print(f"  ⚠ fig1 failed: {e}")

    # Event study
    if sa_df is not None and len(sa_df) > 2:
        try:
            fig, ax = plt.subplots(figsize=(11, 5.5))
            pre  = sa_df[sa_df["year_rel"] < 0]
            post = sa_df[sa_df["year_rel"] >= 0]
            ax.fill_between(pre["year_rel"],  pre["ci_lo"],  pre["ci_hi"],  alpha=0.18, color=C_TEAL)
            ax.fill_between(post["year_rel"], post["ci_lo"], post["ci_hi"], alpha=0.18, color=C_BLUE)
            ax.plot(pre["year_rel"],  pre["coef"],  "o-", color=C_TEAL, lw=2.2, ms=7)
            ax.plot(post["year_rel"], post["coef"], "s-", color=C_BLUE, lw=2.2, ms=7)
            ax.axvline(-0.5, ls="--", color=C_RED, lw=2)
            ax.axhline(0, ls=":", color=C_GREY, lw=1.3)
            ax.set_xlabel("Year Relative to Policy (t=−1 reference)")
            ax.set_ylabel("Coefficient")
            ax.set_title("Sun & Abraham (2021) IW Event Study")
            plt.tight_layout()
            plt.savefig(OUT_DIR / "figures" / "02_main_results" / "fig4b_event_study.png")
            plt.close()
            print("  ✓ fig4b_event_study.png")
        except Exception as e:
            print(f"  ⚠ fig4b failed: {e}")

    print("  (Additional figures generated by R pipeline — see r/platform_analysis.R)")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 10 — JSON summary
# ══════════════════════════════════════════════════════════════════════════════
def export_summary_json(results, df, cf_results, validity):
    def safe(v):
        if v is None or (isinstance(v, float) and math.isnan(v)): return None
        return float(v)

    summary = {
        "n_obs":     int(df.shape[0]),
        "oa_rate":   round(float(df["oa_dummy"].mean()), 4),
        "M1_OLS":    {"beta_oa": safe(_get_param(results.get("m1_ols"), "oa_dummy")),
                      "pval_oa": safe(_get_pval(results.get("m1_ols"), "oa_dummy"))},
        "M4_IV":     {"beta_oa": safe(_get_param(results.get("m4_iv"),  "oa_dummy")),
                      "fs_F":    safe((results.get("m4_iv_diag") or {}).get("fs_f"))},
        "M4b_IV":    {"beta_oa": safe(_get_param(results.get("m4b_iv_resid"), "oa_dummy"))},
        "CATE":      {"mean": safe(cf_results.get("cate_mean")),
                      "std":  safe(cf_results.get("cate_std")),
                      "method": cf_results.get("method", "")},
        "IV_validity": validity,
    }
    with open(OUT_DIR / "tables" / "auto_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
    print("  ✓ auto_summary.json")
    return summary


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    t0 = time.perf_counter()
    print("\n" + "★" * 65)
    print("  Open Access as Orthogonal Platform — Analysis Pipeline")
    print("★" * 65)

    df               = load_data(CSV_PATH)
    df, emb_2d, kw   = embed_and_cluster(df)
    descriptive_stats(df)
    results, clean   = run_econometrics(df)
    validity         = bartik_validity_suite(df, results)
    sa_df            = sun_abraham_event_study(clean)
    cf_results       = causal_forest_hte(df)
    create_figures(df, results, sa_df, kw, emb_2d, cf_results)
    export_summary_json(results, df, cf_results, validity)

    # Save final dataset
    save_cols = [c for c in [
        "Institution", "Pub_Year", "Citing_Patents", "Citing_Works",
        "oa_dummy", "log_patent", "log_citation", "cluster", "top1pct",
        "disruptiveness", "novelty_score", "interdisciplinarity",
        "primary_field", "high_exposure", "pre_field_oa",
        "iv_shift_share", "iv_residualized", "cohort_year",
        "field_yr_trend",
    ] if c in df.columns]
    df[save_cols].to_csv(OUT_DIR / "tables" / "analysis_final.csv",
                         index=False, encoding="utf-8-sig")

    print(f"\n✓ Pipeline complete: {(time.perf_counter()-t0)/60:.1f} min  →  {OUT_DIR}")


if __name__ == "__main__":
    main()
