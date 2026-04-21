# Open Access as an Orthogonal Platform: Knowledge Recombination and Innovation Search in Chinese Research Institutions

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](python/)
[![R](https://img.shields.io/badge/R-4.3%2B-blue)](r/)

## Overview

This repository contains the full replication code and output catalog for an empirical study examining how Open Access (OA) publication functions as a **platform layer** that reshapes knowledge search structure and patent-citation intensity among Chinese research institutions.

Rather than treating OA as a simple visibility shock, this study conceptualizes it as an **orthogonal platform** (Trabucchi & Buganza, 2022; Cusumano et al., 2019) that reorganizes cross-domain knowledge recombination — initially expanding search diversity and later inducing convergence as the platform matures.

---

## Key Findings

| Result | Estimate | Method |
|--------|----------|--------|
| OA level effect (β) | +0.059 – +0.116 | OLS / TWFE / IV-2SLS |
| Stacked DiD ATT (**primary**) | +0.090 (SE=0.015) | Stacked DiD, field-cluster SE |
| Cross-side network effect (mediation) | 32.3% via academic citations | Baron-Kenny + bootstrap |
| Post-2015 convergence (DiD) | −0.083 to −0.172 | TWFE / DiD re-specification |
| GRF ATE (FE-residualized) | +0.073 (SE=0.015) | Causal Forest DML |
| Wild Bootstrap p-value | 0.061 (G=19 cohorts) | Manual Rademacher |
| Permutation p-value | 0.030 | Field-level reassignment |
| Oster δ* (R²_max = 1.37×) | 1.01 (robust threshold) | Oster (2019) |

**Theoretical interpretation:** The negative DiD coefficient is not a contradiction — it is the core theoretical prediction. As OA becomes universal (platform maturation), early-adopter premia converge and differentiation declines. The *level* OA effect remains positive throughout.

---

## Repository Structure

```
.
├── README.md
├── .gitignore
├── LICENSE
│
├── python/
│   └── pipeline.py           # Full Python analysis pipeline
│
├── r/
│   └── platform_analysis.R   # Full R analysis (platform framing + causal ID)
│
└── outputs/
    ├── figures/
    │   ├── 01_descriptive/           # Figs 0, 1, 6 — correlations, trends, institutions
    │   ├── 02_main_results/          # Figs 4b, 4c, 5 — event study, parallel trend, QR
    │   ├── 03_platform_framing/      # Figs A1–A5 — platform typology & value chain
    │   ├── 04_causal_identification/ # Figs B1–B4 — DiD, WCB, HonestDiD, CS-ATT
    │   ├── 05_heterogeneity/         # Figs C1–C3 — causal forest, QR, cluster HTE
    │   ├── 06_robustness/            # Figs D1–D5 — specs, IV (appendix), Conley, Oster
    │   ├── 07_combined/              # Fig F1 — 2×2 summary panel
    │   └── 08_reviewer_fixes/        # Figs R1–R6 — pre-trend joint F, hierarchy, WCB
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

| File | Description |
|------|-------------|
| `01_descriptive/fig0_corr_matrix.png` | Pearson correlation matrix across 11 key variables. Superstar↔Patent Cit.(r=0.52); Disruptiveness↔Acad. Cit.(r=−0.76) |
| `01_descriptive/fig1_annual_trend.png` | Annual paper count (bars) + mean/median patent citations (lines). Post-2015 volume surge but citation convergence |
| `01_descriptive/fig6_institutions.png` | Top-15 Chinese institutions by total and mean patent citations |

### Block 2 — Main Results

| File | Description |
|------|-------------|
| `02_main_results/fig4b_event_study.png` | Sun & Abraham (2021) IW event study. Pre-trends flat; post-policy coefficients mildly negative with widening CI |
| `02_main_results/fig4c_parallel_trend.png` | OA vs Non-OA patent citation gap, 1998–2024. Pre-2015 premium; post-2015 convergence |
| `02_main_results/fig5_quantile.png` | Quantile regression (τ=0.10–0.95). OA and citation effects concentrated in top quantiles |

### Block 3 — Platform Framing

| File | Description |
|------|-------------|
| `03_platform_framing/fig_a1_platform_trajectory.png` | Two-phase OA adoption: Growth (1995–2020) → Consolidation. Non-monotone; S-curve fitting rejected |
| `03_platform_framing/fig_a2_cross_sector_diffusion.png` | Top-8 variance clusters: adoption heterogeneity across research domains |
| `03_platform_framing/fig_a3_cross_side_network_effect.png` | Mediation: 32.3% of OA→patent effect runs through academic citations (bootstrap CI: [0.030, 0.041]) |
| `03_platform_framing/fig_a4_platform_governance_matrix.png` | 2×3 governance matrix (platform maturity × knowledge type). Mature×Disruptive: β=−0.074 (platform lock-in) |
| `03_platform_framing/fig_a5_platform_value_chain.png` | Annual direct/cross-side decomposition. Both pathways decline post-2015 |

### Block 4 — Causal Identification

| File | Description |
|------|-------------|
| `04_causal_identification/fig_b1_stacked_did.png` | **PRIMARY**: Stacked DiD ATT=0.090, field-cluster SE. Pre-trend PASS ✓ |
| `04_causal_identification/fig_b1_ext1_wild_bootstrap.png` | Wild Cluster Bootstrap (G=25, cluster_id): p=0.136; Stacked DiD WCB: p=0.061 |
| `04_causal_identification/fig_b1_ext2_cluster_robustness.png` | β=0.0907 stable across field / HDBSCAN / two-way cluster schemes |
| `04_causal_identification/fig_b1_ext3_honestdid.png` | HonestDiD FLCI (Stacked DiD SE). CI crosses 0 at M≈0.02–0.04 |
| `04_causal_identification/fig_b3_honestdid.png` | Supplementary HonestDiD (manual sensitivity bounds) |
| `04_causal_identification/fig_b4_cs_att.png` | CS-ATT TWFE fallback event study (att_gt convergence failed; panel imbalance disclosed) |

### Block 5 — Heterogeneity

| File | Description |
|------|-------------|
| `05_heterogeneity/fig_c1a_causal_forest_vi.png` | GRF variable importance: lc > fyt > disrupt > novelty > pre_oa |
| `05_heterogeneity/fig_c1b_causal_forest_cate.png` | CATE distribution (ATE_FE=0.073). Concentrated near 0 with right tail |
| `05_heterogeneity/fig_c2_quantile.png` | OA effect: β≈0.01 at τ=0.50, rising to β=0.139 at τ=0.90 |
| `05_heterogeneity/fig_c3_cluster_hte.png` | 88% of 25 research clusters show positive OA effect |

### Block 6 — Robustness (Main + Appendix)

| File | Description |
|------|-------------|
| `06_robustness/fig_d1_specification_forest.png` | OLS/TWFE/FE/IPW/Heckman: β=0.060–0.099, all positive. Oster δ*(1.30×)=0.817 |
| `06_robustness/fig_d2_iv_appendix.png` | IV estimates (Appendix only). IV-LOO β=0.093; Wu-Hausman p=0.85 |
| `06_robustness/fig_d3_conley_bounds.png` | Conley bounds: sign positive for δ≤0.045; CI lower bound crosses 0 at δ=0.005 |
| `06_robustness/fig_d5_external_validity.png` | FE permutation: β=0.066–0.099 across Year/PubType/Country/Field×Year FE |

### Block 7 — Combined Panel

| File | Description |
|------|-------------|
| `07_combined/fig_f1_combined_panel.png` | 2×2 summary: adoption trajectory + cross-side NE + spec robustness + governance typology |

### Block 8 — Reviewer Fixes

| File | Description |
|------|-------------|
| `08_reviewer_fixes/fig_r1_pretrend_joint_test.png` | Extended window (±5yr) Stacked DiD. Joint χ²(4)=4.82, p=0.306 ✓ PASS. Pre/ATT ratio=1.307 |
| `08_reviewer_fixes/fig_r2_identification_hierarchy.png` | ID strategy hierarchy: Stacked DiD=PRIMARY; IV=Appendix (5/9 validity failures) |
| `08_reviewer_fixes/fig_r3_wild_bootstrap_stacked.png` | WCB (G=19 cohorts, stack_cohort_f): p=0.061; Permutation p=0.030 |
| `08_reviewer_fixes/fig_r3b_permutation_dist.png` | Permutation null distribution (R=499). Observed ATT in right tail |
| `08_reviewer_fixes/fig_r4a_dynamic_oa_premium.png` | Annual OA premium β: 0.132 (pre-2015) → 0.052 (post-2015). Platform convergence |
| `08_reviewer_fixes/fig_r4b_did_respecification.png` | Exogenous DiD re-specification (pre_field_oa×post, post_policy=year≥2013) |
| `08_reviewer_fixes/fig_r5_cs_att.png` | CS-ATT TWFE fallback (agg panel, 50% cohort threshold): ATT=0.017 |
| `08_reviewer_fixes/fig_r6_validity_traffic_light.png` | Traffic-light validity summary: PRIMARY ✓ / Pre-trend △ / IV ⚠ (Appendix) / Robustness ✓ |

---

## Methodological Pipeline

### Python Pipeline (`python/pipeline.py`)

| Step | Method | Output |
|------|--------|--------|
| 1 | Data loading + Chinese institution detection | Filtered dataset (N=12,302) |
| 2 | Index construction (IV, FE variables, novelty) | 75-column panel |
| 3 | Sentence embedding (MiniLM-L6-v2) + UMAP + HDBSCAN | 25 research clusters (silhouette=0.364) |
| 4 | Baseline econometrics (OLS, TWFE, IV-2SLS) | Models M1–M12 |
| 5 | Bartik IV validity suite (6 tests) | Validity report |
| 6 | Sun & Abraham IW event study | ES coefficients |
| 7 | Causal Forest HTE (DR-Learner / CausalForestDML) | CATE distribution |
| 8 | Callaway-Sant'Anna ATT | Cohort-level ATT |
| 9 | Heterogeneity sensitivity (Oster bounds) | Partial R² decomposition |
| 10 | Figures, LaTeX tables, JSON summary | All outputs |

### R Pipeline (`r/platform_analysis.R`)

| Block | Method | Key Output |
|-------|--------|------------|
| A | Platform framing (adoption, cross-sector, NE) | Figs A1–A5 |
| B | Stacked DiD + WCB + HonestDiD + CS-ATT | Figs B1–B4 + Ext |
| C | Causal Forest (GRF) + QR + Cluster HTE | Figs C1–C3 |
| D | Oster δ* + IV (Appendix) + Conley + FE permutation | Figs D1–D5 |
| E | modelsummary tables | Tables E1, E4 |
| F | Combined 2×2 panel | Fig F1 |
| R | Reviewer fix suite (joint F, WCB, DiD re-spec, CS-ATT) | Figs R1–R6 |

---

## Requirements

### Python
```
python >= 3.10
numpy, pandas, scipy, statsmodels
linearmodels  # IV-2SLS
sentence-transformers
umap-learn, hdbscan
scikit-learn
econml          # CausalForestDML (optional)
torch
matplotlib, seaborn
```

### R
```r
# Core
dplyr, readr, stringr, tidyr, purrr, forcats
ggplot2, ggrepel, scales, patchwork, RColorBrewer, viridis

# Econometrics
fixest, ivreg, AER, sandwich, lmtest
quantreg, sensemakr

# Causal inference
did          # Callaway-Sant'Anna
HonestDiD    # Rambachan & Roth (2023)
grf          # Causal Forest
bacondecomp  # Goodman-Bacon

# Inference
fwildclusterboot  # Wild Cluster Bootstrap
boot
Rglpk        # LP solver for HonestDiD

# Output
broom, modelsummary, flextable, officer
```

---

## Identification Strategy Summary

The paper uses **Stacked DiD as the primary identification strategy**, exploiting staggered OA adoption timing across research fields. Bartik IV results are reported in the Appendix only, due to pre-trend violations (p=0.002) and Goldsmith-Pinkham exposure-β correlation exceeding the 0.30 threshold (r=0.504). Wu-Hausman p=0.850 confirms endogeneity is not a material concern.

| Strategy | Role | β | Note |
|----------|------|---|------|
| Stacked DiD | **PRIMARY** | 0.090 | Field-cluster SE; pre-trend ✓ |
| TWFE / FE permutation | Supporting | 0.059–0.099 | Sign consistent |
| HonestDiD | Sensitivity bounds | — | CI robust to M≤0.02 |
| GRF Causal Forest | Exploratory HTE | 0.073 | FE-residualized |
| IV-2SLS | **Appendix only** | 0.116 | Pre-trend FAIL; GP corr=0.504 |

---

## Theoretical Framing

The paper extends platform typology (Trabucchi & Buganza, 2022; Cusumano et al., 2019) by positioning OA as an **orthogonal platform**:

- One side (researchers) receives direct value (discoverability)
- Other side (patent inventors) benefits indirectly via knowledge recombination
- No direct transaction occurs between sides
- Value extraction: asymmetric, through knowledge spillovers

**Convergence prediction:** As OA penetration exceeds ~67% (observed 2020 peak), early-adopter differentiation collapses. The negative DiD coefficient (post-2015) reflects *platform maturation*, not OA harm.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
