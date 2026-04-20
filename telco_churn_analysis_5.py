import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# ------------------------------------------------------------------
# 1. PATHS
# ------------------------------------------------------------------
DATA_PATH = Path(r"D:\ALL PROJECTS\N8N\DATA ANALYSIS\Dataset\Telco_customer_churn.xlsx")

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR    = SCRIPT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

if not DATA_PATH.exists():
    sys.exit(
        f"ERROR: Cannot find the dataset at:\n  {DATA_PATH}\n"
        f"Edit DATA_PATH at the top of this script to point at the file."
    )

# ==================================================================
# 2. USER INPUT STEP  (runs BEFORE any data processing / analysis)
# ==================================================================
print("=" * 70)
print("TELCO CHURN ANALYST  -  Input-Driven Analysis")
print("=" * 70)
print("Examples of queries you can ask:")
print("  - Analyze churn across contract types")
print("  - Identify top and bottom segments by total charges")
print("  - Compare senior vs non-senior churn behavior")
print("  - Evaluate monthly charges vs churn")
print("  - Identify key factors influencing churn")
print("  (Press Enter for the default: charges by contract type.)")
print()
user_query = input("Enter the type of analysis or insights you want from the dataset: ")

# ------------------------------------------------------------------
# 3. LOAD + CLEAN  (shared by every analysis mode)
# ------------------------------------------------------------------
df = pd.read_excel(DATA_PATH)

# Normalize column names: lowercase, underscores, no spaces
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# total_charges has 11 blank strings (tenure-0 customers) -> coerce to 0
df["total_charges"] = pd.to_numeric(df["total_charges"], errors="coerce").fillna(0)

# Defensive dedup on customer id
df = df.drop_duplicates(subset="customerid")

# Tenure buckets (plain hyphens - safe on every terminal encoding)
def tenure_bucket(m):
    if m <= 12:  return "0-12 mo"
    if m <= 24:  return "13-24 mo"
    if m <= 48:  return "25-48 mo"
    return "49-72 mo"

df["tenure_group"] = df["tenure_months"].apply(tenure_bucket)

# ------------------------------------------------------------------
# 4. QUERY INTERPRETER
#    Parses the free-text query into { mode, dimension } so the
#    analysis + charts can adapt automatically.
# ------------------------------------------------------------------
# keyword-in-query  ->  dataset column used for grouping
DIMENSION_MAP = {
    "contract":          "contract",
    "payment":           "payment_method",
    "internet":          "internet_service",
    "senior":            "senior_citizen",
    "tenure":            "tenure_group",
    "gender":            "gender",
    "partner":           "partner",
    "dependent":         "dependents",
    "phone service":     "phone_service",
    "multiple line":     "multiple_lines",
    "paperless":         "paperless_billing",
    "online security":   "online_security",
    "online backup":     "online_backup",
    "device protection": "device_protection",
    "tech support":      "tech_support",
    "streaming tv":      "streaming_tv",
    "streaming movie":   "streaming_movies",
    "streaming":         "streaming_tv",
}

CHURN_WORDS   = ("churn", "leaving", "attrition", "retention", "retain")
CHARGES_WORDS = ("charge", "revenue", "contribute", "top", "bottom", "earning", "billing")
FACTORS_WORDS = ("key factor", "driver", "influence", "imbalance", "overall")

def interpret_query(q):
    raw = (q or "").strip()
    ql  = raw.lower()

    # First, find the segmentation dimension the user mentioned (if any).
    dim = None
    for kw, col in DIMENSION_MAP.items():
        if kw in ql:
            dim = col
            break

    has_churn   = any(w in ql for w in CHURN_WORDS)
    has_charges = any(w in ql for w in CHARGES_WORDS)
    has_factors = any(w in ql for w in FACTORS_WORDS)

    # Decide the analysis mode.
    if has_factors and has_churn:
        return {"mode": "key_factors",      "dimension": None,              "raw": raw}
    if has_churn and has_charges:
        return {"mode": "charges_vs_churn", "dimension": None,              "raw": raw}
    if has_churn:
        return {"mode": "churn_by_segment", "dimension": dim or "contract", "raw": raw}
    # Default (also handles empty input): preserve ORIGINAL behavior.
    return {"mode": "charges_by_segment",   "dimension": dim or "contract", "raw": raw}

intent = interpret_query(user_query)

# ------------------------------------------------------------------
# 5. STYLE + SHARED HELPERS
# ------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.titleweight": "bold",
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})
PALETTE = ["#2E86AB", "#A23B72", "#F18F01", "#3F8E44", "#7D4F9B", "#D1495B"]

def segment_report(frame, col, metric="total_charges"):
    g = frame.groupby(col, observed=True)[metric].agg(["sum", "mean", "count"])
    g.columns = ["total_contribution", "avg_contribution", "customers"]
    return g.sort_values("total_contribution", ascending=False)

def order_if_tenure(obj, dim):
    if dim == "tenure_group":
        return obj.reindex(["0-12 mo", "13-24 mo", "25-48 mo", "49-72 mo"])
    return obj

def pretty(col):
    return col.replace("_", " ").title()

# ==================================================================
# 6. ANALYSIS MODES
#    Each function prints its own report + saves 3 charts (bar/pie/line).
# ==================================================================

# ------- MODE A: charges_by_segment (ORIGINAL BEHAVIOR PRESERVED) ---
def run_charges_by_segment(df, dim):
    total_revenue = df["total_charges"].sum()
    n_customers   = len(df)

    seg = segment_report(df, dim)
    seg["pct_share"] = 100 * seg["total_contribution"] / total_revenue
    if dim == "tenure_group":
        seg = order_if_tenure(seg, dim)

    # Preserve original dual-view when the dim is 'contract'
    tenure_seg = None
    if dim == "contract":
        tenure_seg = segment_report(df, "tenure_group")
        tenure_seg["pct_share"] = 100 * tenure_seg["total_contribution"] / total_revenue
        tenure_seg = order_if_tenure(tenure_seg, "tenure_group")

    top_seg    = seg["total_contribution"].idxmax()
    bottom_seg = seg["total_contribution"].idxmin()

    print("=" * 70)
    print(f"TELCO CHARGES CONTRIBUTION  -  by {pretty(dim).upper()}")
    print("=" * 70)
    print(f"Customers analyzed : {n_customers:,}")
    print(f"Total charges (USD): ${total_revenue:,.2f}")
    print(f"Avg charges / cust : ${df['total_charges'].mean():,.2f}")
    print(f"\n--- By {pretty(dim)} ---")
    print(seg.round(2).to_string())
    if tenure_seg is not None:
        print("\n--- By Tenure group ---")
        print(tenure_seg.round(2).to_string())
    print(f"\nHighest contributor : {top_seg}  "
          f"(${seg.loc[top_seg,'total_contribution']:,.0f}, "
          f"{seg.loc[top_seg,'pct_share']:.1f}%)")
    print(f"Lowest contributor  : {bottom_seg}  "
          f"(${seg.loc[bottom_seg,'total_contribution']:,.0f}, "
          f"{seg.loc[bottom_seg,'pct_share']:.1f}%)")

    # ---- Bar chart ----
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(seg.index.astype(str), seg["total_contribution"] / 1e6,
                  color=PALETTE[:len(seg)], edgecolor="white", linewidth=1.5)
    ax.set_title(f"Total Charges by {pretty(dim)}")
    ax.set_xlabel(pretty(dim))
    ax.set_ylabel("Total Charges (USD, millions)")
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("$%.2fM"))
    for b, v in zip(bars, seg["total_contribution"]):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                f"${v/1e6:.2f}M", ha="center", va="bottom", fontsize=10)
    ax.set_ylim(0, seg["total_contribution"].max() / 1e6 * 1.15)
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    bar_name = "bar_chart_contract_revenue.png" if dim == "contract" else f"bar_chart_{dim}_revenue.png"
    plt.savefig(OUT_DIR / bar_name, dpi=150, bbox_inches="tight"); plt.close()

    # ---- Pie chart ----
    fig, ax = plt.subplots(figsize=(7, 7))
    _, _, autotexts = ax.pie(
        seg["total_contribution"], labels=seg.index.astype(str),
        autopct="%1.1f%%", colors=PALETTE[:len(seg)], startangle=90,
        wedgeprops=dict(edgecolor="white", linewidth=2),
        textprops=dict(fontsize=11),
    )
    for at in autotexts:
        at.set_color("white"); at.set_fontweight("bold")
    ax.set_title(f"Revenue Share by {pretty(dim)}", pad=15)
    plt.tight_layout()
    pie_name = "pie_chart_contract_share.png" if dim == "contract" else f"pie_chart_{dim}_share.png"
    plt.savefig(OUT_DIR / pie_name, dpi=150, bbox_inches="tight"); plt.close()

    # ---- Line chart (avg monthly charges vs tenure - ORIGINAL) ----
    trend = (df.groupby("tenure_months")["monthly_charges"]
               .mean().reset_index().sort_values("tenure_months"))
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(trend["tenure_months"], trend["monthly_charges"],
            color=PALETTE[0], linewidth=2.2, marker="o",
            markersize=4, markerfacecolor=PALETTE[1], markeredgecolor="white")
    ax.set_title("Average Monthly Charges vs. Customer Tenure")
    ax.set_xlabel("Tenure (Months)")
    ax.set_ylabel("Average Monthly Charges (USD)")
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("$%.0f"))
    ax.grid(alpha=0.25, linestyle="--")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "line_chart_tenure_trend.png", dpi=150, bbox_inches="tight"); plt.close()

    print("\nCharts saved:")
    print(f"  - {bar_name}")
    print(f"  - {pie_name}")
    print( "  - line_chart_tenure_trend.png")


# ------- MODE B: churn_by_segment ----------------------------------
def run_churn_by_segment(df, dim):
    g = df.groupby(dim, observed=True)["churn_value"].agg(["mean", "count", "sum"])
    g.columns = ["churn_rate", "customers", "churned"]
    g["churn_rate_pct"] = 100 * g["churn_rate"]
    g = order_if_tenure(g, dim) if dim == "tenure_group" else g.sort_values("churn_rate", ascending=False)

    overall = df["churn_value"].mean() * 100
    top_seg    = g["churn_rate"].idxmax()
    bottom_seg = g["churn_rate"].idxmin()

    print("=" * 70)
    print(f"TELCO CHURN ANALYSIS  -  by {pretty(dim).upper()}")
    print("=" * 70)
    print(f"Customers         : {len(df):,}")
    print(f"Overall churn rate: {overall:.1f}%")
    print(f"\n--- Churn rate by {pretty(dim)} ---")
    print(g.round(3).to_string())
    print(f"\nHighest churn : {top_seg}  "
          f"({g.loc[top_seg,'churn_rate_pct']:.1f}%, "
          f"{int(g.loc[top_seg,'churned'])}/{int(g.loc[top_seg,'customers'])})")
    print(f"Lowest churn  : {bottom_seg}  "
          f"({g.loc[bottom_seg,'churn_rate_pct']:.1f}%, "
          f"{int(g.loc[bottom_seg,'churned'])}/{int(g.loc[bottom_seg,'customers'])})")

    # Bar: churn rate per segment (with overall baseline)
    fig, ax = plt.subplots(figsize=(8.5, 5))
    bars = ax.bar(g.index.astype(str), g["churn_rate_pct"],
                  color=PALETTE[:len(g)], edgecolor="white", linewidth=1.5)
    ax.axhline(overall, color="#555", linestyle="--", linewidth=1,
               label=f"Overall {overall:.1f}%")
    ax.set_title(f"Churn Rate by {pretty(dim)}")
    ax.set_xlabel(pretty(dim)); ax.set_ylabel("Churn Rate (%)")
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.0f%%"))
    for b, v in zip(bars, g["churn_rate_pct"]):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                f"{v:.1f}%", ha="center", va="bottom", fontsize=10)
    ax.legend(frameon=False, loc="upper right")
    plt.xticks(rotation=15, ha="right"); plt.tight_layout()
    plt.savefig(OUT_DIR / f"bar_chart_churn_by_{dim}.png", dpi=150, bbox_inches="tight"); plt.close()

    # Pie: share of churned customers by segment
    fig, ax = plt.subplots(figsize=(7, 7))
    _, _, autotexts = ax.pie(
        g["churned"], labels=g.index.astype(str),
        autopct="%1.1f%%", colors=PALETTE[:len(g)], startangle=90,
        wedgeprops=dict(edgecolor="white", linewidth=2),
        textprops=dict(fontsize=11),
    )
    for at in autotexts:
        at.set_color("white"); at.set_fontweight("bold")
    ax.set_title(f"Share of Churned Customers by {pretty(dim)}", pad=15)
    plt.tight_layout()
    plt.savefig(OUT_DIR / f"pie_chart_churn_share_{dim}.png", dpi=150, bbox_inches="tight"); plt.close()

    # Line: churn rate vs tenure_months
    trend = df.groupby("tenure_months")["churn_value"].mean().reset_index().sort_values("tenure_months")
    trend["churn_pct"] = trend["churn_value"] * 100
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(trend["tenure_months"], trend["churn_pct"],
            color=PALETTE[0], linewidth=2.2, marker="o", markersize=4,
            markerfacecolor=PALETTE[1], markeredgecolor="white")
    ax.set_title("Churn Rate vs. Customer Tenure")
    ax.set_xlabel("Tenure (Months)"); ax.set_ylabel("Churn Rate (%)")
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.0f%%"))
    ax.grid(alpha=0.25, linestyle="--"); plt.tight_layout()
    plt.savefig(OUT_DIR / "line_chart_churn_vs_tenure.png", dpi=150, bbox_inches="tight"); plt.close()

    print("\nCharts saved:")
    print(f"  - bar_chart_churn_by_{dim}.png")
    print(f"  - pie_chart_churn_share_{dim}.png")
    print( "  - line_chart_churn_vs_tenure.png")


# ------- MODE C: charges_vs_churn ----------------------------------
def run_charges_vs_churn(df):
    g = df.groupby("churn_label", observed=True).agg(
        customers=("customerid", "count"),
        avg_monthly=("monthly_charges", "mean"),
        total_revenue=("total_charges", "sum"),
    )
    churned_rev  = float(g.loc["Yes", "total_revenue"]) if "Yes" in g.index else 0.0
    retained_rev = float(g.loc["No",  "total_revenue"]) if "No"  in g.index else 0.0
    total_rev    = churned_rev + retained_rev

    print("=" * 70)
    print("TELCO CHARGES vs CHURN ANALYSIS")
    print("=" * 70)
    print(g.round(2).to_string())
    if "Yes" in g.index and "No" in g.index:
        diff = g.loc["Yes", "avg_monthly"] - g.loc["No", "avg_monthly"]
        print(f"\nChurned customers pay ${g.loc['Yes','avg_monthly']:.2f}/mo on average")
        print(f"Retained customers pay ${g.loc['No','avg_monthly']:.2f}/mo on average")
        print(f"Difference: ${diff:+.2f}/mo "
              f"({'churned pay more' if diff>0 else 'retained pay more'})")
    print(f"Revenue share attributable to already-churned customers: "
          f"{churned_rev/total_rev*100:.1f}% of ${total_rev:,.0f}")

    # Bar: avg monthly charges by churn status
    colors = [PALETTE[5] if x == "Yes" else PALETTE[0] for x in g.index]
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(g.index.astype(str), g["avg_monthly"],
                  color=colors, edgecolor="white", linewidth=1.5)
    ax.set_title("Average Monthly Charges: Churned vs Retained")
    ax.set_xlabel("Churn"); ax.set_ylabel("Avg Monthly Charges (USD)")
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("$%.0f"))
    for b, v in zip(bars, g["avg_monthly"]):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                f"${v:.0f}", ha="center", va="bottom", fontsize=11)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "bar_chart_charges_vs_churn.png", dpi=150, bbox_inches="tight"); plt.close()

    # Pie: lifetime revenue share retained vs churned
    fig, ax = plt.subplots(figsize=(7, 7))
    _, _, autotexts = ax.pie(
        [retained_rev, churned_rev], labels=["Retained", "Churned"],
        autopct="%1.1f%%", colors=[PALETTE[0], PALETTE[5]], startangle=90,
        wedgeprops=dict(edgecolor="white", linewidth=2),
        textprops=dict(fontsize=11),
    )
    for at in autotexts:
        at.set_color("white"); at.set_fontweight("bold")
    ax.set_title("Lifetime Revenue Share: Retained vs Churned", pad=15)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "pie_chart_revenue_by_churn.png", dpi=150, bbox_inches="tight"); plt.close()

    # Line: avg monthly charges vs tenure, split by churn label
    pivot = (df.groupby(["tenure_months", "churn_label"], observed=True)["monthly_charges"]
               .mean().unstack("churn_label").sort_index())
    fig, ax = plt.subplots(figsize=(9, 5))
    if "No" in pivot.columns:
        ax.plot(pivot.index, pivot["No"], color=PALETTE[0], linewidth=2.2,
                marker="o", markersize=3, label="Retained")
    if "Yes" in pivot.columns:
        ax.plot(pivot.index, pivot["Yes"], color=PALETTE[5], linewidth=2.2,
                marker="s", markersize=3, label="Churned")
    ax.set_title("Avg Monthly Charges vs. Tenure, by Churn Status")
    ax.set_xlabel("Tenure (Months)"); ax.set_ylabel("Avg Monthly Charges (USD)")
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("$%.0f"))
    ax.grid(alpha=0.25, linestyle="--"); ax.legend(frameon=False); plt.tight_layout()
    plt.savefig(OUT_DIR / "line_chart_charges_by_churn_tenure.png", dpi=150, bbox_inches="tight"); plt.close()

    print("\nCharts saved:")
    print("  - bar_chart_charges_vs_churn.png")
    print("  - pie_chart_revenue_by_churn.png")
    print("  - line_chart_charges_by_churn_tenure.png")


# ------- MODE D: key_factors ---------------------------------------
def run_key_factors(df):
    overall = df["churn_value"].mean() * 100
    FACTORS = ["contract", "internet_service", "payment_method", "tenure_group",
               "senior_citizen", "paperless_billing", "partner", "dependents"]

    rows = []
    for f in FACTORS:
        if f not in df.columns:
            continue
        rates = df.groupby(f, observed=True)["churn_value"].mean() * 100
        rates = order_if_tenure(rates, f) if f == "tenure_group" else rates.sort_values(ascending=False)
        rows.append({
            "factor":        f,
            "worst_segment": f"{rates.idxmax()} ({rates.max():.1f}%)",
            "best_segment":  f"{rates.idxmin()} ({rates.min():.1f}%)",
            "churn_gap_pp":  float(rates.max() - rates.min()),
        })
    factors_df = pd.DataFrame(rows).sort_values("churn_gap_pp", ascending=False)

    print("=" * 70)
    print("TELCO KEY CHURN FACTORS  -  RANKED BY CHURN-RATE DISPARITY")
    print("=" * 70)
    print(f"Overall churn rate: {overall:.1f}%  (baseline)")
    print("\n--- Factors ranked by gap between worst and best segment ---")
    print(factors_df.round(2).to_string(index=False))
    top = factors_df.iloc[0]
    print(f"\nStrongest driver: {top['factor']}  (gap {top['churn_gap_pp']:.1f}pp; "
          f"worst: {top['worst_segment']} vs best: {top['best_segment']})")

    # Bar (horizontal): churn-rate gap per factor
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(factors_df["factor"].str.replace("_", " ").str.title(),
                   factors_df["churn_gap_pp"],
                   color=PALETTE[:len(factors_df)], edgecolor="white", linewidth=1.5)
    ax.set_title("Churn-Rate Disparity by Factor  (worst segment - best segment)")
    ax.set_xlabel("Churn-rate gap (percentage points)")
    for b, v in zip(bars, factors_df["churn_gap_pp"]):
        ax.text(b.get_width(), b.get_y() + b.get_height() / 2,
                f"  {v:.1f}pp", va="center", fontsize=10)
    ax.invert_yaxis(); plt.tight_layout()
    plt.savefig(OUT_DIR / "bar_chart_key_factors.png", dpi=150, bbox_inches="tight"); plt.close()

    # Pie: overall base - retained vs churned
    churned  = int(df["churn_value"].sum())
    retained = len(df) - churned
    fig, ax = plt.subplots(figsize=(7, 7))
    _, _, autotexts = ax.pie(
        [retained, churned], labels=["Retained", "Churned"],
        autopct="%1.1f%%", colors=[PALETTE[0], PALETTE[5]], startangle=90,
        wedgeprops=dict(edgecolor="white", linewidth=2),
        textprops=dict(fontsize=11),
    )
    for at in autotexts:
        at.set_color("white"); at.set_fontweight("bold")
    ax.set_title("Overall Customer Base: Retained vs Churned", pad=15)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "pie_chart_overall_churn.png", dpi=150, bbox_inches="tight"); plt.close()

    # Line: churn rate vs tenure (the single strongest signal)
    trend = df.groupby("tenure_months")["churn_value"].mean().reset_index().sort_values("tenure_months")
    trend["churn_pct"] = trend["churn_value"] * 100
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(trend["tenure_months"], trend["churn_pct"],
            color=PALETTE[0], linewidth=2.2, marker="o", markersize=4,
            markerfacecolor=PALETTE[1], markeredgecolor="white")
    ax.axhline(overall, color="#555", linestyle="--", linewidth=1,
               label=f"Overall {overall:.1f}%")
    ax.set_title("Churn Rate vs. Tenure")
    ax.set_xlabel("Tenure (Months)"); ax.set_ylabel("Churn Rate (%)")
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.0f%%"))
    ax.grid(alpha=0.25, linestyle="--"); ax.legend(frameon=False); plt.tight_layout()
    plt.savefig(OUT_DIR / "line_chart_churn_vs_tenure.png", dpi=150, bbox_inches="tight"); plt.close()

    print("\nCharts saved:")
    print("  - bar_chart_key_factors.png")
    print("  - pie_chart_overall_churn.png")
    print("  - line_chart_churn_vs_tenure.png")


# ==================================================================
# 7. DISPATCH  (route to the right mode based on the interpreted query)
# ==================================================================
print("\n" + "#" * 70)
print(f"USER QUERY  : {intent['raw'] if intent['raw'] else '(empty - using default)'}")
label = f"mode={intent['mode']}"
if intent["dimension"]:
    label += f", dimension={intent['dimension']}"
print(f"INTERPRETED : {label}")
print("#" * 70 + "\n")

if intent["mode"] == "charges_by_segment":
    run_charges_by_segment(df, intent["dimension"])
elif intent["mode"] == "churn_by_segment":
    run_churn_by_segment(df, intent["dimension"])
elif intent["mode"] == "charges_vs_churn":
    run_charges_vs_churn(df)
elif intent["mode"] == "key_factors":
    run_key_factors(df)

print(f"\nAll outputs saved to: {OUT_DIR}")
