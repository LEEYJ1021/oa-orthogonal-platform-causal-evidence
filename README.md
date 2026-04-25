# Open Access as an Orthogonal Platform: Causal Evidence on Knowledge Recombination and Platform Convergence

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](python/)
[![R](https://img.shields.io/badge/R-4.3%2B-blue)](r/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.placeholder.svg)](https://doi.org/)
[![Replication](https://img.shields.io/badge/Replication-Full-brightgreen)]()
[![Data](https://img.shields.io/badge/Data-Lens.org-orange)](https://lens.org)
[![Pre--registration](https://img.shields.io/badge/Pre--trend%20test-p%3D0.850-success)]()

---

## Overview

This repository contains the complete, fully reproducible replication archive for an empirical study examining how **Open Access (OA) publication infrastructure reshapes cross-domain knowledge recombination and science-to-technology transfer** among China's leading research institutions (1995–2024).

The study makes two interrelated contributions:

1. **Theoretical**: It reconceptualizes OA publishing infrastructure as an *orthogonal platform* — a non-priced, asymmetric architecture connecting transportation researchers (Side 1) and patent inventors (Side 2) through cross-side network effects, without direct interaction between groups. This extends platform theory beyond digital intermediation and market governance into institutionally governed knowledge infrastructure.

2. **Empirical**: Using 12,045 patent-cited papers from China's top 33 research institutions across 25 semantic research clusters, it provides causally identified evidence of a **two-phase trajectory**: an early *access expansion* phase in which OA confers a positive patent citation premium (ATT = +0.090), followed by a *platform convergence* phase (post-2015) in which near-universal adoption erodes early-adopter differentiation and compresses the adoption premium — a dynamic that platform maturation theory predicts endogenously, without auxiliary assumptions.

> **Core interpretive point.** The negative post-2015 DiD coefficient is not evidence that OA harms knowledge transfer. It is the theoretical *signature* of platform convergence: the structural basis for comparative OA advantage disappears as OA approaches the modal publication format, shifting the binding constraint on inventor search from *access* to *attention*. The level effect of OA remains positive throughout the observation window.

---

## Key Results at a Glance

| Estimand | Estimate | SE | Method | Role |
|---|---|---|---|---|
| OA level effect (ATT) | **+0.090** | 0.015 | Stacked DiD | **Primary** |
| OA level effect range | +0.059 – +0.099 | — | OLS / TWFE / IPW / Heckman | Supporting |
| GRF ATE (FE-residualized) | +0.073 | 0.015 | Causal Forest DML | Exploratory |
| Cross-side mediation share | **32.3%** | Bootstrap CI: [0.030, 0.041] | Baron-Kenny + bootstrap | Architecture-consistent |
| Post-2015 DiD (endogenous) | −0.108 | 0.048 | TWFE interaction | Convergence H2 |
| Post-2015 DiD (exogenous) | −0.172 | 0.081 | Pre-field OA rate × post | Convergence H2 (preferred) |
| Wild cluster bootstrap *p* | 0.061 | G=19 cohorts | Manual Rademacher | Inference supplement |
| Permutation *p* | **0.030** | R=499 | Field-level reassignment | Inference supplement |
| Oster δ* (R²_max = 1.37×) | **1.01** | — | Oster (2019) | OV robustness |
| Pre-trend joint test (±3yr) | χ²(2) = 0.326, **p = 0.850** | — | Stacked DiD | **PASS** |
| Pre-trend joint test (±5yr) | χ²(4) = 4.82, **p = 0.306** | — | Stacked DiD | **PASS** |
| Superstar OA odds ratio | 1.84 | — | Logistic, top-1% outcome | Anti-dilution evidence |

---

## Theoretical Framework

### OA as an Orthogonal Platform

The study applies the orthogonal platform typology (Cusumano et al., 2019; Trabucchi & Buganza, 2022) to OA scientific publishing. Three constitutive structural conditions are satisfied:

| Condition | OA Publishing Instantiation |
|---|---|
| **Asymmetric, non-interacting user groups** | Researchers (Side 1) produce, pay APCs, respond to mandates. Patent inventors (Side 2) consume without any platform participation. |
| **Non-transactional value transfer** | No price, contract, or exchange connects paper authors to citing patent inventors. Value flows through knowledge content only. |
| **Cross-side network effects** | Growth in Side 1 OA adoption expands the recombination pool accessible to Side 2 inventors, raising the probability of encounter with relevant scientific inputs. |

OA publishing represents an **institutional variant** of orthogonal platform architecture — value flows governed by funder mandates, copyright frameworks, and publisher policies rather than market mechanisms. This distinguishes it from market-governed orthogonal platforms (e.g., Google Search, Strava) and generates distinct convergence dynamics.

### Two-Phase Trajectory

```
Phase 1 — Access Expansion (OA penetration low → rising)
  OA creates asymmetric accessibility → cross-side network effect → positive citation premium
  H1: β₁ > 0 ✓ confirmed (ATT = +0.090)

Phase 2 — Platform Convergence (OA penetration → modal adoption ~67%)
  Differentiation collapse: OA advantage erodes as participation approaches universality
  Attention concentration: binding constraint shifts from access to attention
  H2: β₂ < 0 ✓ confirmed (DiD = −0.108 to −0.172)

H3: Attenuation ∝ pre-existing field-level OA penetration (not generic temporal trend) ✓ supported
```

The key predictive distinction: diffusion-based accounts require auxiliary congestion/displacement terms to generate penetration-indexed attenuation. The platform framework generates it **endogenously** from maturation dynamics — a falsifiable structural difference, not merely a relabeling.

---

## Data

| Attribute | Value |
|---|---|
| Source | [Lens.org](https://lens.org) (open-access bibliometric repository, 200M+ records) |
| Query | Keyword "Transportation" in title/abstract/keywords |
| Institution filter | China's top 33 research institutions (985/211 & CAS; see Appendix A.1) |
| Publication window | 1992–2024 (analysis window: 1995–2024) |
| Patent citation filter | ≥ 1 citing patent (science-to-technology transfer intensive margin) |
| Pre-exclusion sample | 12,302 records (92.1% retention from 13,349 raw) |
| **Analysis sample** | **12,045 papers** (after removing missing values on estimation variables) |
| Research clusters | 25 semantic clusters (MiniLM-L6-v2 → UMAP → HDBSCAN, silhouette = 0.364) |
| OA adoption rate | 57.1% of sample |
| Mean patent citations | 2.056 (SD = 3.978; max = 159) |
| Platform maturity variable | Pre-field OA rate: mean = 0.501 (SD = 0.303) |

### Institution Coverage

China's 985/211 universities and the Chinese Academy of Sciences account for approximately 70% of the country's scientific output and represent the tier with deepest exposure to national OA mandates and broadest access to APC funding. OA adoption timing varies substantially across institutions and clusters within this group, providing the within-sample variation required for causal identification.

> Full institution list: see `outputs/tables/table_a1_institutions.csv`

### Research Cluster Structure

The 25 clusters span the full technology stack of contemporary transportation innovation across six functional groups:

| Functional Group | Clusters | Platform Maturity |
|---|---|---|
| Autonomous & intelligent systems | C8, C12, C16 | Mature |
| Traffic flow & prediction | C23, C24 | Mature |
| Electrification | C3, C4, C17, C21 | Mature |
| Energy & materials | C10, C11, C20, C22 | Mature |
| Civil & structural infrastructure | C0, C2, C7 | Emerging |
| Connectivity, logistics, environmental | C1, C5, C13 | Mixed |

Six nominally biomedical clusters (C6, C9, C14, C15, C18, C19) are retained; patent linkage examination confirms they connect predominantly to autonomous vehicle biosensing, wearable driver-fatigue monitoring, and bioinspired lightweight materials.

---

## Repository Structure

```
.
├── README.md
├── LICENSE
├── .gitignore
│
├── python/
│   └── pipeline.py                  # Full Python analysis pipeline (Steps 1–10)
│
├── r/
│   └── platform_analysis.R          # Full R analysis pipeline (Blocks A–R)
│
└── outputs/
    ├── figures/
    │   ├── 01_descriptive/           # Correlation matrix, annual trend, institutions
    │   ├── 02_main_results/          # Event study, parallel trend, quantile regression
    │   ├── 03_platform_framing/      # Platform typology, value chain decomposition
    │   ├── 04_causal_identification/ # Stacked DiD, WCB, HonestDiD, CS-ATT fallback
    │   ├── 05_heterogeneity/         # Causal forest, CATE, cluster-level HTE
    │   ├── 06_robustness/            # Specification forest, IV (appendix), Conley, Oster
    │   ├── 07_combined/              # 2×2 summary panel
    │   └── 08_reviewer_fixes/        # Pre-trend extension, WCB, DiD re-spec, validity summary
    │
    └── tables/
        ├── table1_descriptive.csv
        ├── table_main_results.tex
        ├── table_gp_decomp.csv
        ├── table_superstar.csv
        ├── table_platform_governance.csv
        ├── table_cluster_robustness.csv
        ├── table_oster_sensitivity.csv
        ├── table_did_respecification.csv
        ├── table_policy_cutoff_sensitivity.csv
        ├── table_cs_att_comparison.csv
        ├── table_iv_validity_formal.csv
        ├── table_pretrend_joint_test.csv
        └── table_validity_report_full.csv
```

---

## Figure Catalog

### Block 1 — Descriptive

| Figure | Description |
|---|---|
| `01_descriptive/fig0_corr_matrix.png` | Pearson correlation matrix across 11 key variables. Notable: Superstar ↔ Patent Citations (r = 0.52); Disruptiveness ↔ Academic Citations (r = −0.76), confirming disruptive papers trade breadth for depth. |
| `01_descriptive/fig1_annual_trend.png` | Annual paper count (bars, left axis) + mean/median patent citations (lines, right axis), 1995–2024. Post-2015 volume surge with simultaneous citation convergence — the dual dynamic motivating the empirical approach. |
| `01_descriptive/fig6_institutions.png` | Top-15 Chinese institutions by total patent-cited papers (left, blue) and mean patent citation count per paper (right, teal). CAS leads in volume; Fudan, Peking, and Nanjing lead in per-paper impact. Volume–impact heterogeneity motivates field-clustered SE throughout. |

### Block 2 — Main Results

| Figure | Description |
|---|---|
| `02_main_results/fig4b_event_study.png` | Sun & Abraham (2021) interaction-weighted event study. Pre-period coefficients flat and jointly insignificant; post-policy response mildly positive with widening CI consistent with heterogeneous treatment timing. |
| `02_main_results/fig4c_parallel_trend.png` | Calendar-year mean patent citations for OA vs. Non-OA papers (1998–2024) with OA–Non-OA gap (lower panel). Pre-2015 premium visible; post-2015 convergence toward parity. Note: unconditional group means; not a formal parallel-trends test (see event study residuals). |
| `02_main_results/fig5_quantile.png` | Quantile regression (τ = 0.50–0.95) for log(academic citations) (left, blue) and OA (right, green), year-demeaned. OA effect negligible at median; rises to β ≈ 0.19 at τ = 0.95. Upper-tail amplification consistent with cross-side network effect operating multiplicatively with scientific visibility. |

### Block 3 — Platform Framing

| Figure | Description |
|---|---|
| `03_platform_framing/fig_a1_platform_trajectory.png` | Two-phase OA adoption trajectory: Growth phase (1995–2020) → Consolidation. Non-monotone; cluster-level penetration exceeds 60% from 2015, peaks at 66.8% in 2020. |
| `03_platform_framing/fig_a2_cross_sector_diffusion.png` | Top-8 variance clusters showing adoption heterogeneity across research domains — the cross-cluster variation exploited by staggered DiD identification. |
| `03_platform_framing/fig_a3_cross_side_network_effect.png` | Mediation decomposition: 32.3% of total OA effect travels through academic citations (bootstrap 95% CI: [0.030, 0.041]). Direct pathway: β = 0.075 (67.7%). Treated as architecture-consistent structural evidence; not causal identification. |
| `03_platform_framing/fig_a4_platform_governance_matrix.png` | 2×3 governance matrix (platform maturity × knowledge type). Key cells: Emerging × Incremental: β = +0.070*** (access expansion active); Mature × Interdisciplinary: β = +0.117 (cross-boundary access sensitivity persists); Mature × Disruptive: β = −0.074 (directionally consistent with platform lock-in, p = 0.096). |
| `03_platform_framing/fig_a5_platform_value_chain.png` | Annual decomposition of OA effect into direct (red, OA→Patent) and cross-side (blue, OA→AcadCit→Patent) pathways, 2000–2024. Both pathways decline post-2015. n-weighted annual cross-side share: 34.4%; global model: 32.3%. Stability of share supports structural rather than cohort-specific interpretation. |

### Block 4 — Causal Identification

| Figure | Description |
|---|---|
| `04_causal_identification/fig_b1_stacked_did.png` | **PRIMARY ESTIMATOR.** Stacked DiD event study (±3yr window; t = −1 reference). Pre-trend coefficients jointly insignificant: χ²(2) = 0.326, p = 0.850 ✓. Post-treatment coefficients consistently positive; t = +3 significant at p = 0.036. ATT = +0.090 (SE = 0.015, field-clustered). N = 20,444 across 19 treated cohorts. |
| `04_causal_identification/fig_r1_pretrend_joint_test.png` | **Extended ±5yr event study.** Joint pre-trend: χ²(4) = 4.82, p = 0.306 ✓ PASS. Pre/ATT ratio = 1.307 (t = −5 magnitude / post ATT). Pre-period coefficients trend monotonically toward zero as t → −1, consistent with differential pre-levels rather than diverging pre-trends. HonestDiD bounds address the ratio concern directly. |
| `04_causal_identification/fig_b1_ext2_cluster_robustness.png` | β = 0.0907 exactly stable across three clustering schemes: field-level (N = 1,414; SE = 0.028), HDBSCAN research cluster (N = 25; SE = 0.032), and two-way field × year (SE = 0.023). All significant at p < 0.01 or better. |
| `04_causal_identification/fig_b1_ext3_honestdid.png` | HonestDiD FLCI sensitivity bounds (Rambachan & Roth, 2023) for M ∈ [0.00, 0.12]. Post-period ATT remains above zero for M ≤ 0.12, a bound substantially exceeding the observed t = −2 pre-trend coefficient magnitude (small; CI includes zero). |
| `04_causal_identification/fig_b1_ext1_wild_bootstrap.png` | Inference comparison: Permutation test (R = 499 field-level reassignments) p = 0.030 ✓; Wild Cluster Bootstrap (G = 19 cohorts, R = 2,999 Rademacher draws) p = 0.061 △. Borderline WCB p reflects low cohort count (G < 30), not weak effect — consistent with Roodman et al. (2019) simulation evidence. |
| `04_causal_identification/fig_r3b_permutation_dist.png` | Permutation null distribution (R = 499). Distribution centered near zero (mean ≈ 0.000, SD ≈ 0.030). Observed ATT of +0.075 falls in the empirical upper tail (solid red line); two-sided p = 0.030. Symmetric null rules out field-level compositional confounds. |
| `04_causal_identification/fig_r2_identification_hierarchy.png` | Identification strategy hierarchy. Stacked DiD = PRIMARY (ATT = +0.0905); TWFE/FE permutation = SUPPORTING (β = 0.0591); GRF = EXPLORATORY (ATE = 0.073); IV-2SLS = APPENDIX ONLY (5/9 validity checks fail). |
| `04_causal_identification/fig_b4_cs_att.png` | Callaway–Sant'Anna TWFE fallback event study (CS-ATT formal estimator failed due to extreme panel imbalance; median obs./unit = 3). Fallback ATT = +0.017 (SE = 0.050) — directionally consistent with primary estimate; downward bias expected under extreme imbalance and known TWFE forbidden comparisons. |

### Block 5 — Heterogeneous Treatment Effects

| Figure | Description |
|---|---|
| `05_heterogeneity/fig_c1a_causal_forest_vi.png` | GRF CausalForest variable importance (FE-residualized; 5-fold cross-fitting; N = 5,000 subsample). Top predictors of CATE: log(academic citations) > field-year trend > disruptiveness > novelty > pre-field OA rate. Pre-field OA rate at rank 5 is structurally consistent with H3 (platform maturity as governance-relevant moderator). |
| `05_heterogeneity/fig_c1b_causal_forest_cate.png` | CATE distribution (full FE-residualized sample, blue; trimmed [0.05, 0.95], teal). Concentrated near zero with right tail. ATE = 0.073. Top-decile CATEs correspond disproportionately to autonomous systems (C12, C16) and electrification (C3, C4) — theoretically predicted domains of highest cross-domain recombination intensity. |
| `05_heterogeneity/fig_c2_quantile.png` | OA quantile regression: β ≈ 0.00 at τ = 0.50; rising to β ≈ 0.19 at τ = 0.95. OLS benchmark (β ≈ 0.067) lies between 75th and 90th percentile estimates. Upper-tail concentration inconsistent with pure quality-dilution account; consistent with cross-side network effects amplifying returns to already-visible papers. |
| `05_heterogeneity/fig_c3_cluster_hte.png` | Cluster-level OA coefficients from 25 separate within-cluster OLS regressions (year FE; robust SE). 22/25 clusters (88%) show positive OA effect (blue). Three negative clusters — C12 (LiDAR/perception), C1 (air quality), C4 (battery chemistry) — are all platform-mature with above-median pre-field OA rates, directly consistent with H2 convergence prediction. |

### Block 6 — Robustness

| Figure | Description |
|---|---|
| `06_robustness/fig_d1_specification_forest.png` | Specification robustness: OA coefficient across six estimators — TWFE+PubType FE (β = 0.099), IPW-TWFE (β = 0.087), OLS (β = 0.072), TWFE Field×Year (β = 0.066), TWFE Field+Year (β = 0.061), Heckman (β = 0.060). All positive; all 95% CIs exclude zero. Oster δ*(R²_max = 1.37×) = 1.01 ✓. |
| `06_robustness/fig_d2_iv_appendix.png` | IV estimates (supplementary directional evidence only). IV-Bartik: β = +0.064 (p = 0.034); IV-LOO: β = +0.093 (p < 0.001). Both positive and directionally consistent with primary ATT. Reported in appendix only: 5/9 Bartik validity checks fail (pre-trend violations p < 0.01; GP exposure-β correlation r = 0.504 > 0.30 threshold). Wu-Hausman p = 0.850 (OLS and IV indistinguishable; interpret with caution given instrument invalidity). |
| `06_robustness/fig_d3_conley_bounds.png` | Conley (1999) spatial HAC bounds for IV-2SLS estimate across δ ∈ [0.00, 0.10]. Point estimate positive for δ ≤ 0.045; CI lower bound crosses zero at δ = 0.005. IV-specific analysis only; Stacked DiD identification unaffected by spatial autocorrelation concern. |
| `06_robustness/fig_d5_external_validity.png` | FE permutation across alternative fixed effect specifications: Year FE, PubType FE, Country FE, Field×Year FE. β range: 0.066–0.099; all positive. |

### Block 7 — Combined Summary Panel

| Figure | Description |
|---|---|
| `07_combined/fig_f1_combined_panel.png` | 2×2 summary: (top-left) OA adoption trajectory; (top-right) cross-side network effect mediation; (bottom-left) specification robustness forest; (bottom-right) governance heterogeneity typology. |

### Block 8 — Reviewer-Oriented Supplementary Figures

| Figure | Description |
|---|---|
| `08_reviewer_fixes/fig_r4a_dynamic_oa_premium.png` | Annual OA patent citation premium (β) from cross-sectional OLS with field, year, and field×year trend controls, 2000–2024. Pre-2015 n-weighted mean: β = 0.132 (teal). Post-2015 mean: β = 0.052 (amber). Systematic downward trend consistent with platform convergence. Premium remains positive throughout (does not cross zero), confirming level effect persists while differential premium attenuates. |
| `08_reviewer_fixes/fig_r4b_did_respecification.png` | DiD convergence estimates across three specifications: endogenous OA dummy × post (β = −0.108, p = 0.025); exogenous pre-field OA rate × post (β = −0.172, p = 0.035, preferred); binary high-exposure × post (β = −0.153, p = 0.008). All negative and statistically significant. Policy cutoff sensitivity confirms negative interaction coefficients across 2012–2015 cutoffs. |
| `08_reviewer_fixes/fig_r6_validity_traffic_light.png` | Traffic-light identification validity summary across five dimensions: Primary ID (Stacked DiD) ✓ STRONG; Pre-trend Tests △ MARGINAL (jointly insignificant; HonestDiD robust to M ≤ 0.12); IV ⚠ APPENDIX ONLY; Robustness Checks ✓ STRONG; Theory ✓ RESOLVED (negative DiD + positive level effect jointly consistent with platform convergence). |
| `08_reviewer_fixes/fig_a5_platform_value_chain.png` | Annual direct vs. cross-side pathway decomposition (stacked area, upper panel) and cross-side share % (lower panel). n-weighted annual mean share: 34.4%; global model: 32.3%. LOESS-smoothed annual trend shows no systematic drift, supporting structural rather than cohort-specific interpretation. |

---

## Methodological Pipeline

### Python Pipeline (`python/pipeline.py`)

| Step | Method | Key Output |
|---|---|---|
| 1 | Data loading and Chinese institution detection (regex on affiliation strings) | Filtered dataset (N = 12,302) |
| 2 | Index construction: IV (Bartik shift-share), FE variables, novelty, disruptiveness, interdisciplinarity | 75-column panel |
| 3 | MiniLM-L6-v2 sentence embedding (384-dim) → UMAP (15D cluster, 2D visualization) → HDBSCAN (mcs = 123; silhouette = 0.364) | 25 research clusters |
| 4 | Baseline econometrics: OLS, TWFE (field+year, field×year), IPW-TWFE, Heckman selection | Models M1–M12 |
| 5 | Bartik IV validity suite (9 tests: pre-trend, GP correlation, LOFO, falsification, Wu-Hausman) | Validity report (Table B2) |
| 6 | Sun & Abraham (2021) interaction-weighted event study | Event study coefficients |
| 7 | Causal Forest HTE with FE residualization (DR-Learner / CausalForestDML, 5-fold) | CATE distribution + variable importance |
| 8 | Callaway-Sant'Anna ATT (formal estimator + TWFE fallback) | Cohort-level ATT |
| 9 | Oster (2019) proportional selection bounds across R²_max multipliers (1.05×–2.00×) | δ* sensitivity table |
| 10 | Figure generation, LaTeX table export, JSON validity summary | All outputs |

### R Pipeline (`r/platform_analysis.R`)

| Block | Estimator / Package | Key Output |
|---|---|---|
| **A** | Platform framing: adoption trajectory, cross-sector diffusion, mediation (Baron-Kenny, boot R=1,500) | Figures A1–A5 |
| **B** | `did` (Stacked DiD) + `fwildclusterboot` (WCB, G=19, R=2,999) + `HonestDiD` (FLCI) + CS-ATT fallback | Figures B1–B4 + Extensions |
| **C** | `grf` (CausalForest, FE-residualized, 5-fold) + `quantreg` + cluster-level OLS (N=25 regressions) | Figures C1–C3 |
| **D** | `sensemakr` (Oster δ*) + IV-2SLS (appendix, Bartik + LOO) + Conley HAC + FE permutation (R=500) | Figures D1–D5 |
| **E** | `modelsummary` / `flextable` formatted regression tables | Tables E1, E4 |
| **F** | `patchwork` 2×2 combined summary panel | Figure F1 |
| **R** | Reviewer fix suite: extended event study (±5yr), identification hierarchy, WCB comparison, DiD re-specification, CS-ATT TWFE fallback, validity traffic light | Figures R1–R6 |

---

## Identification Strategy

### Primary: Stacked Difference-in-Differences

The primary identification exploits **staggered OA adoption timing across 25 semantic research clusters**, estimated via the Stacked DiD design of Baker et al. (2022) and Cengiz et al. (2019).

**Why Stacked DiD over TWFE?** Goodman-Bacon (2021) shows that TWFE under staggered adoption generates "forbidden comparisons" — early-adopting clusters serve as controls while their treatment effects are still evolving. This concern is acute here because platform maturation theory predicts treatment effects changing sign over time (H2). Stacked DiD delivers clean ATT estimates without imposing balanced panels or homogeneous treatment effect dynamics.

**Cohort definition:** Year in which cluster-level OA adoption first exceeds 50%. For each cohort *g*, a sub-dataset combines the treated cluster with clean controls (never-treated clusters and clusters with cohort > g+3) over a symmetric ±3-year event window. Stack-cohort × field and stack-cohort × year fixed effects absorb cohort-specific confounds.

| Diagnostic | Result | Assessment |
|---|---|---|
| Pre-trend joint test (±3yr): χ²(2) | 0.326, p = 0.850 | ✓ PASS |
| Pre-trend joint test (±5yr): χ²(4) | 4.82, p = 0.306 | ✓ PASS |
| HonestDiD robustness bound | Positive for M ≤ 0.12 | ✓ ROBUST |
| Cluster robustness (3 schemes) | β = 0.0907, SE 0.023–0.032 | ✓ STABLE |
| Permutation test (R=499) | p = 0.030 | ✓ PASS |
| Wild cluster bootstrap (G=19) | p = 0.061 | △ MARGINAL (low G) |
| Oster δ* (R²_max = 1.37×) | 1.01 | ✓ ROBUST |

### Identification Strategy Hierarchy

```
PRIMARY       Stacked DiD              ATT = +0.090  ✓ Pre-trend PASS; WCB p=0.061; Perm p=0.030
SUPPORTING    TWFE / FE permutation    β = +0.059 to +0.099  All positive
EXPLORATORY   GRF Causal Forest        ATE = +0.073  FE-residualized; right-skewed CATE
APPENDIX ONLY IV-2SLS (Bartik)         β = +0.064   5/9 validity checks fail — directional only
```

> **On the Bartik IV.** Five of nine exclusion restriction validation checks are not satisfied: pre-trend violations (p = 0.002 and p < 0.001), Goldsmith-Pinkham exposure-β correlation (r = 0.504, threshold 0.30), and two falsification failures. IV estimates are confined to the appendix as supplementary directional evidence only. The Wu-Hausman test (p = 0.850) indicates OLS and IV estimates are statistically indistinguishable, but should be interpreted with caution given instrument invalidity. No causal claim in the main analysis rests on IV estimates.

---

## Alternative Explanations and Mechanism Discrimination

The three most plausible alternative accounts are systematically ruled out:

| Alternative | Prediction | Evidence | Assessment |
|---|---|---|---|
| **Quality dilution** | Attenuation uniform across citation distribution; lower OA effects for high-quality papers | Attenuation persists within novelty/disruptiveness terciles; OA superstar odds ratio = 1.84 (opposite direction) | ✗ Rejected |
| **Citation window truncation** | Convergence concentrated in most recent cohorts | Fixed 5-year exposure window shows same pattern; Recent indicator and field×year trend included | ✗ Rejected |
| **Cohort composition** | Level shifts across cohorts, not penetration-indexed attenuation | Attenuation specifically tied to pre-field OA rate; cohort-matched subsamples confirm | ✗ Rejected |
| **Platform convergence** | Attenuation indexed to field-level OA penetration; stronger for mature fields; persists across citation windows; upper-tail amplification | All three confirmed simultaneously | ✓ Consistent |

---

## Governance Implications

The two-phase trajectory generates phase-sensitive policy implications that depart from universal-mandate approaches:

- **Access-expansion phase** (emerging fields: C0 asphalt, C2 cement, C7 infrastructure): OA mandates generate positive cross-side returns; expansion remains the appropriate policy lever.
- **Platform convergence phase** (mature fields: C12 LiDAR, C16 traffic control, C4 battery chemistry): The binding constraint has shifted from *access* to *attention*. Interventions targeting citation signal quality — structured metadata, knowledge graph integration, machine-readable licensing, persistent identifier infrastructure — may generate larger cross-side spillovers than additional access mandates.
- **Policy evaluation implication**: Average treatment effect estimates pooled across the full adoption lifecycle systematically understate early-phase benefits while overstating marginal returns to continued mandate expansion at late stages.

---

## Requirements

### Python
```
python >= 3.10
numpy
pandas
scipy
statsmodels
linearmodels          # IV-2SLS, TWFE
sentence-transformers # MiniLM-L6-v2 embeddings
umap-learn
hdbscan
scikit-learn
econml                # CausalForestDML (optional)
torch
matplotlib
seaborn
```

### R (≥ 4.3.0)
```r
# Data wrangling
dplyr, readr, stringr, tidyr, purrr, forcats, lubridate

# Visualization
ggplot2, ggrepel, scales, patchwork, RColorBrewer, viridis

# Panel econometrics
fixest           # TWFE with multi-way clustering
ivreg            # IV-2SLS
AER
sandwich         # Heteroskedasticity-robust SE
lmtest
quantreg         # Quantile regression
sensemakr        # Oster (2019) proportional selection bounds

# Causal DiD
did              # Callaway-Sant'Anna (2021)
bacondecomp      # Goodman-Bacon decomposition
HonestDiD        # Rambachan and Roth (2023) FLCI bounds

# Machine learning
grf              # Generalized Random Forests / Causal Forest

# Small-sample inference
fwildclusterboot # Wild Cluster Bootstrap (Roodman et al., 2019)
boot

# LP solver (HonestDiD)
Rglpk

# Output
broom
modelsummary
flextable
officer
```

---

## Reproducibility

The full pipeline (Python + R) is self-contained within this repository. All figures and tables in the paper and appendix can be reproduced from the raw data extract using the scripts in `/python/` and `/r/` in sequence.

**Execution order:**
1. `python/pipeline.py` — data processing, clustering, all econometric models, raw figure exports
2. `r/platform_analysis.R` — platform framing figures, causal DiD suite, causal forest, robustness, combined panels

**Runtime:** Approximately 45–90 minutes on a standard laptop (sentence embedding and causal forest are the bottlenecks; GPU acceleration optional for embedding step).

**Random seeds:** Set globally at the top of both scripts for full numerical reproducibility.

---

## Key References

| Reference | Role in Paper |
|---|---|
| Cusumano, M.A., Gawer, A., & Yoffie, D.B. (2019). *The Business of Platforms.* HarperBusiness. | Orthogonal platform typology |
| Trabucchi, D. & Buganza, T. (2022). Landlords with no lands. *European Journal of Innovation Management*, 25(6), 64–96. | Structural conditions for orthogonal platform classification |
| Baker, A.C., Larcker, D.F., & Wang, C.C.Y. (2022). How much should we trust staggered DiD estimates? *Journal of Financial Economics*, 144(2), 370–395. | Primary DiD estimator |
| Callaway, B. & Sant'Anna, P.H.C. (2021). DiD with multiple time periods. *Journal of Econometrics*, 225(2), 200–230. | CS-ATT (fallback; convergence failure disclosed) |
| Rambachan, A. & Roth, J. (2023). A more credible approach to parallel trends. *Review of Economic Studies*, 90(5), 2555–2591. | HonestDiD sensitivity bounds |
| Goodman-Bacon, A. (2021). DiD with variation in treatment timing. *Journal of Econometrics*, 225(2), 254–277. | TWFE bias motivation |
| Roodman, D. et al. (2019). Fast and wild. *Stata Journal*, 19(1), 4–60. | Wild Cluster Bootstrap, small-G behavior |
| Oster, E. (2019). Unobservable selection and coefficient stability. *Journal of Business & Economic Statistics*, 37(2), 187–204. | Proportional selection bounds |
| Evans, D.S. (2008). The economics of the online advertising industry. *Review of Network Economics*, 7(3). | Attention concentration mechanism |
| Fleming, L. (2001). Recombinant uncertainty in technological search. *Management Science*, 47(1), 117–132. | Knowledge recombination theory |

---

## License

MIT License — see [LICENSE](LICENSE) for full terms. Data sourced from [Lens.org](https://lens.org) under their open data terms; bibliometric records remain subject to Lens.org's data use policy.
