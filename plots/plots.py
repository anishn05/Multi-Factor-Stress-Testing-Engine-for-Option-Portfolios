import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", context="talk")


def plot_scenario_dashboard(
    scenario_name,
    base_spot,
    shocked_spot,
    true_pnl,
    pnl_breakdown,
    spot_path=None,
    convexity_threshold=0.03,
):
    """
    2x2 scenario dashboard
    """

    fig, axes = plt.subplots(2, 2, figsize=(12, 7))
    fig.suptitle(f"Stress & PnL Explain", fontsize=18, weight="bold")

    # ===============================
    # 1️⃣ Spot Move Visualization
    # ===============================
    ax = axes[0, 0]
    sns.lineplot(
        x=[0, 1],
        y=[base_spot, shocked_spot],
        marker="o",
        ax=ax,
        color="tab:blue"
    )
    ax.set_title("Spot Shock")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Base", "Shocked"])
    ax.set_ylabel("Spot Level")
    ax.axhline(base_spot, linestyle="--", alpha=0.6)
    ax.axhline(shocked_spot, linestyle="--", alpha=0.6)

    # ===============================
    # 2️⃣ PnL Attribution Bar Chart
    # ===============================
    ax = axes[0, 1]

    components = ["Delta Pnl", "Gamma Pnl", "Vega Pnl", "Theta Pnl"]
    values = [pnl_breakdown[c] for c in components]

    sns.barplot(
        x=components,
        y=values,
        palette="Set2",
        ax=ax
    )

    ax.axhline(0, color="black", linewidth=1)
    ax.set_title("PnL Attribution (Greeks)")
    ax.set_ylabel("PnL")
    ax.tick_params(axis="x", rotation=20)

    # ===============================
    # 3️⃣ Explain vs True PnL + Error Band
    # ===============================
    ax = axes[1, 0]

    explained_pnl = (
        pnl_breakdown["Delta Pnl"]
        + pnl_breakdown["Gamma Pnl"]
        + pnl_breakdown["Vega Pnl"]
        + pnl_breakdown["Theta Pnl"]
    )

    pnl_values = [explained_pnl, true_pnl]
    labels = ["Explained PnL", "True PnL"]

    sns.barplot(
        x=labels,
        y=pnl_values,
        palette=["tab:green", "tab:red"],
        ax=ax
    )

    error = true_pnl - explained_pnl
    ax.errorbar(
        x=0,
        y=explained_pnl,
        yerr=abs(error),
        fmt="none",
        ecolor="black",
        capsize=6,
        label="Residual Error"
    )

    ax.set_title("PnL Explain vs Full Revaluation")
    ax.set_ylabel("PnL")
    ax.legend()

    # ===============================
    # 4️⃣ Convexity & Model Validity Flags
    # ===============================
    ax = axes[1, 1]

    spot_move_pct = abs(shocked_spot / base_spot - 1.0)
    gamma_ratio = abs(pnl_breakdown["Gamma Pnl"]) / max(
        abs(pnl_breakdown["Delta Pnl"]), 1e-6
    )

    flags = {
        "Large Spot Move": spot_move_pct > convexity_threshold,
        "Gamma Dominant": gamma_ratio > 1.0,
        "Large Residual": abs(pnl_breakdown["Residual"]) > 0.2 * abs(true_pnl),
    }

    colors = ["tab:red" if v else "tab:green" for v in flags.values()]

    sns.barplot(
        x=list(flags.keys()),
        y=[1 if v else 0 for v in flags.values()],
        palette=colors,
        ax=ax
    )

    ax.set_ylim(0, 1.2)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["OK", "FLAG"])
    ax.set_title("Model Validity & Convexity Flags")
    ax.tick_params(axis="x", rotation=15)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    return fig
