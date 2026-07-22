"""
Part 2 — reusable grayscale forest-plot module + flagged structural bug fix
=============================================================================
(D) Appendix Figure E3 (cluster-level heterogeneity) label inconsistency:
    The submitted appendix labels clusters as "14: Virology", "21: Cluster 21",
    "23: Deep learning" — these do NOT match the canonical cluster names in
    Table A2 of the SAME manuscript (C14 = COVID/SARS-CoV research,
    C21 = Li-ion battery chemistry, C23 = spatiotemporal traffic forecasting).
    This is an internal consistency error a careful reviewer will catch
    immediately (two figures/tables in the same paper naming the same
    cluster ID two different things). We cannot regenerate the real
    HDBSCAN cluster assignments (that intermediate file/pipeline is not
    part of this data pull), so instead we ship the harmonization utility
    below: it forces every cluster-level figure to pull its label from a
    SINGLE canonical source (Table A2), so this class of bug becomes
    structurally impossible to reintroduce.

Below that, a reusable grayscale forest-plot function is applied to two
supporting figures using the ESTIMATES ALREADY REPORTED IN THE MANUSCRIPT
TEXT (Table B1 / Appendix D.3) — i.e., a format conversion of disclosed
numbers, not new computation — as a template the authors can point at
their own stacked-DiD output arrays for the remaining appendix figures.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5,
    "axes.edgecolor": "black", "axes.linewidth": 0.9,
    "axes.grid": True, "grid.color": "0.85", "grid.linewidth": 0.6,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
})
GRAY_DARK = "0.15"

# -----------------------------------------------------------------------
# (D) Canonical cluster-label registry — SINGLE SOURCE OF TRUTH
# Populate this from Table A2 exactly once; every figure imports from here.
# This is what was missing: Appendix E3 apparently pulled labels from a
# different, stale keyword-extraction pass instead of this table.
# -----------------------------------------------------------------------
CANONICAL_CLUSTER_LABELS = {
    "C0":  "Asphalt / pavement",
    "C1":  "Emissions / air quality",
    "C2":  "Cement / concrete",
    "C3":  "EV charging",
    "C4":  "Battery state estimation",
    "C5":  "Maritime / collision risk",
    "C7":  "Tunnels / bridges",
    "C8":  "Pavement defect detection",
    "C12": "LiDAR / perception",
    "C13": "IoT / V2X connectivity",
    "C14": "COVID / SARS transit response",     # NOT "Virology"
    "C16": "Traffic control / driving",
    "C17": "Power electronics",
    "C20": "Battery thermal management",
    "C21": "Li-ion battery chemistry",           # NOT "Cluster 21"
    "C22": "Fuel-cell catalysts",
    "C23": "Spatiotemporal traffic forecasting", # NOT "Deep learning"
    "C24": "Urban mobility optimization",
    # ... complete for all 25 IDs from Table A2 before regenerating Fig. E3
}

def cluster_label(cluster_id: str) -> str:
    """Single lookup point — guarantees every figure agrees with Table A2."""
    if cluster_id not in CANONICAL_CLUSTER_LABELS:
        raise KeyError(
            f"{cluster_id} has no entry in Table A2 registry — "
            "add it before plotting, do not invent a label ad hoc."
        )
    return f"{cluster_id}: {CANONICAL_CLUSTER_LABELS[cluster_id]}"


# -----------------------------------------------------------------------
# Reusable grayscale forest plot
# -----------------------------------------------------------------------
def grayscale_forest(labels, betas, ses, pvals=None, title="", xlabel="Coefficient (95% CI)",
                      ref_line=0.0, figsize=(7.2, None), fname=None, note=None):
    """
    labels : list[str]            row labels, top-to-bottom as given
    betas  : array-like            point estimates
    ses    : array-like            standard errors
    pvals  : array-like or None    used only to bold/mark significant rows
    Encodes significance via marker fill (filled = p<.05) rather than colour.
    """
    betas = np.asarray(betas, dtype=float)
    ses = np.asarray(ses, dtype=float)
    n = len(labels)
    h = figsize[1] or max(2.2, 0.55 * n + 1.2)
    fig, ax = plt.subplots(figsize=(figsize[0], h))
    ypos = np.arange(n)[::-1]

    sig = np.array([p < 0.05 for p in pvals]) if pvals is not None else np.ones(n, dtype=bool)
    for i in range(n):
        mfc = GRAY_DARK if sig[i] else "white"
        ax.errorbar(betas[i], ypos[i], xerr=1.96 * ses[i], fmt="o",
                    mfc=mfc, mec="black", mew=1.3, ms=8,
                    ecolor="black" if sig[i] else "0.55",
                    elinewidth=1.6 if sig[i] else 1.1, capsize=3, ls="none", zorder=3)
        ax.annotate(f"{betas[i]:+.3f}", xy=(betas[i], ypos[i]), xytext=(0, 9),
                    textcoords="offset points", ha="center", fontsize=8.3, color="0.2")

    ax.axvline(ref_line, color="black", lw=0.8)
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels)
    ax.set_xlabel(xlabel)
    ax.set_title(title, fontsize=10.5, loc="left")
    ax.set_ylim(-0.8, n - 0.2)

    leg = [
        Line2D([0], [0], marker="o", mfc=GRAY_DARK, mec="black", ms=8, ls="none", label="p < .05"),
        Line2D([0], [0], marker="o", mfc="white", mec="black", ms=8, ls="none", label="n.s."),
    ]
    ax.legend(handles=leg, loc="best", fontsize=8.5, frameon=True, edgecolor="0.5")
    if note:
        fig.text(0.02, -0.02, note, fontsize=8, color="0.3", ha="left")
    fig.tight_layout()
    if fname:
        fig.savefig(fname, dpi=300, bbox_inches="tight")
    plt.close(fig)


# --- Applied example 1: Appendix B1 (IV estimates) using DISCLOSED numbers ---
grayscale_forest(
    labels=["IV–Leave-one-out", "IV–Residualized (Borusyak)", "IV–Bartik (primary supplementary)"],
    betas=[0.093, 0.389, 0.064],
    ses=[0.027, 0.179, 0.037],
    pvals=[0.000, 0.030, 0.034],
    title="Appendix Fig. B1 (regenerated). IV estimates — supplementary,\nnot part of primary identification (5/9 exclusion checks fail; §3.5.1)",
    xlabel="OA coefficient, β (95% CI)",
    fname="figs/Fig_B1_regenerated_grayscale.png",
    note="Note: values as reported in Table B1 of the manuscript (Bartik/Borusyak/LOO IV, HC-robust SE).\n"
         "Re-rendered for print/B&W compliance only — no re-estimation performed here.",
)

# --- Applied example 2: Appendix D.3 (cluster-robustness) using DISCLOSED numbers ---
grayscale_forest(
    labels=["Two-way (Field × Year)", "Research cluster (HDBSCAN)", "Field cluster"],
    betas=[0.0907, 0.0907, 0.0907],
    ses=[0.0234, 0.0316, 0.0281],
    pvals=[0.001, 0.01, 0.01],
    title="Appendix Fig. D2 (regenerated). Stacked-DiD ATT is identical across\nclustering schemes — only precision (SE) differs",
    xlabel="DiD ATT (95% CI)",
    fname="figs/Fig_D2_regenerated_grayscale.png",
    note="Note: values as reported in Appendix D.3 of the manuscript. Re-rendered for print/B&W\n"
         "compliance only. Template for regenerating remaining colour figures (event study, HonestDiD,\n"
         "permutation null, GRF importance, quantile regression, ID hierarchy, mediation decomposition):\n"
         "call grayscale_forest(labels=..., betas=..., ses=..., pvals=...) with YOUR OWN estimation output.",
)

print("Wrote figs/Fig_B1_regenerated_grayscale.png and figs/Fig_D2_regenerated_grayscale.png")
print("\nCanonical cluster registry has", len(CANONICAL_CLUSTER_LABELS), "of 25 IDs populated —")
print("fill in the rest from Table A2 before regenerating Appendix Fig. E3.")
