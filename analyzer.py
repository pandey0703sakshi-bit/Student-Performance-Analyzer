# ============================================================
# STUDENT PERFORMANCE ANALYZER
# Author  : Your Name
# Date    : April 2026
# Tech    : Python | Pandas | Matplotlib | Seaborn
# Purpose : Analyze student academic data, identify at-risk
#           students, generate visualizations and a report.
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import datetime


# ============================================================
# CONFIGURATION — change thresholds here without touching code
# ============================================================

DATA_PATH          = "data/students.csv"
CHARTS_DIR         = "charts"
REPORT_PATH        = "report.txt"
TOP_AVG_THRESHOLD  = 80    # minimum average to be a top performer
TOP_ATT_THRESHOLD  = 85    # minimum attendance to be a top performer
RISK_AVG_THRESHOLD = 50    # average below this = at-risk
RISK_ATT_THRESHOLD = 65    # attendance below this = at-risk
GOOD_ATTENDANCE    = 75    # used for attendance impact analysis


# ============================================================
# STEP 1: LOAD DATA
# ============================================================

def load_data(path):
    """Load student CSV into a DataFrame and add Average column."""
    df = pd.read_csv(path)
    df["Average"] = df[["Math", "Science", "English"]].mean(axis=1).round(2)
    return df


# ============================================================
# STEP 2: ANALYSIS
# ============================================================

def analyse(df):
    """Run all analysis and return results as a dictionary."""

    subject_avgs = {
        "Math"    : df["Math"].mean().round(2),
        "Science" : df["Science"].mean().round(2),
        "English" : df["English"].mean().round(2),
    }

    top_performers = df[
        (df["Average"] >= TOP_AVG_THRESHOLD) &
        (df["Attendance"] >= TOP_ATT_THRESHOLD)
    ]

    at_risk = df[
        (df["Average"] < RISK_AVG_THRESHOLD) |
        (df["Attendance"] < RISK_ATT_THRESHOLD)
    ]

    good_att_avg = df[df["Attendance"] >= GOOD_ATTENDANCE]["Average"].mean().round(2)
    poor_att_avg = df[df["Attendance"] <  GOOD_ATTENDANCE]["Average"].mean().round(2)
    att_gap      = round(good_att_avg - poor_att_avg, 2)
    correlation  = df["Attendance"].corr(df["Average"]).round(2)

    pass_rate    = round(len(df[df["Average"] >= RISK_AVG_THRESHOLD]) / len(df) * 100, 1)
    attend_rate  = round(len(df[df["Attendance"] >= GOOD_ATTENDANCE]) / len(df) * 100, 1)

    weakest   = min(subject_avgs, key=subject_avgs.get)
    strongest = max(subject_avgs, key=subject_avgs.get)

    if correlation >= 0.7:
        corr_strength = "strong positive"
    elif correlation >= 0.4:
        corr_strength = "moderate positive"
    else:
        corr_strength = "weak"

    return {
        "subject_avgs"  : subject_avgs,
        "top_performers": top_performers,
        "at_risk"       : at_risk,
        "good_att_avg"  : good_att_avg,
        "poor_att_avg"  : poor_att_avg,
        "att_gap"       : att_gap,
        "correlation"   : correlation,
        "corr_strength" : corr_strength,
        "pass_rate"     : pass_rate,
        "attend_rate"   : attend_rate,
        "weakest"       : weakest,
        "strongest"     : strongest,
    }


# ============================================================
# STEP 3: VISUALIZATIONS
# ============================================================

def create_charts(df, results):
    """Generate and save all 4 charts to the charts/ folder."""

    os.makedirs(CHARTS_DIR, exist_ok=True)
    sns.set_theme(style="whitegrid")
    avgs = results["subject_avgs"]

    # ── Chart 1: Subject averages bar chart ───────────────
    subjects = list(avgs.keys())
    values   = list(avgs.values())
    colors   = ["#378ADD", "#1D9E75", "#E24B4A"]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(subjects, values, color=colors, width=0.5, edgecolor="white")

    for bar, val in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            str(val),
            ha="center", va="bottom", fontsize=12, fontweight="bold"
        )

    plt.title("Subject-wise Class Averages", fontsize=15, fontweight="bold", pad=15)
    plt.xlabel("Subject", fontsize=12)
    plt.ylabel("Average Marks (out of 100)", fontsize=12)
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig(f"{CHARTS_DIR}/01_subject_averages.png", dpi=150)
    plt.close()

    # ── Chart 2: Heatmap ──────────────────────────────────
    heatmap_data = df.set_index("Name")[["Math", "Science", "English"]]

    plt.figure(figsize=(8, 10))
    sns.heatmap(
        heatmap_data,
        annot=True, fmt="d",
        cmap="RdYlGn",
        linewidths=0.5, linecolor="white",
        vmin=0, vmax=100
    )
    plt.title("Student vs Subject Performance Heatmap", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Subject", fontsize=12)
    plt.ylabel("Student Name", fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{CHARTS_DIR}/02_heatmap.png", dpi=150)
    plt.close()

    # ── Chart 3: Score distribution histogram ─────────────
    plt.figure(figsize=(8, 5))
    plt.hist(df["Average"], bins=10, color="#7F77DD", edgecolor="white", linewidth=0.8)
    plt.axvline(x=RISK_AVG_THRESHOLD, color="#E24B4A", linestyle="--",
                linewidth=1.5, label=f"At-risk threshold ({RISK_AVG_THRESHOLD})")
    plt.axvline(x=TOP_AVG_THRESHOLD,  color="#1D9E75", linestyle="--",
                linewidth=1.5, label=f"Top performer threshold ({TOP_AVG_THRESHOLD})")
    plt.axvline(df["Average"].mean(), color="orange", linestyle="-",
                linewidth=2, label=f"Class mean ({df['Average'].mean().round(1)})")
    plt.title("Distribution of Student Averages", fontsize=15, fontweight="bold", pad=15)
    plt.xlabel("Average Marks", fontsize=12)
    plt.ylabel("Number of Students", fontsize=12)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(f"{CHARTS_DIR}/03_score_distribution.png", dpi=150)
    plt.close()

    # ── Chart 4: Attendance vs performance scatter ─────────
    point_colors = df["Average"].apply(
        lambda avg: "#E24B4A" if avg < RISK_AVG_THRESHOLD
                    else ("#1D9E75" if avg >= TOP_AVG_THRESHOLD else "#378ADD")
    )

    plt.figure(figsize=(8, 5))
    plt.scatter(df["Attendance"], df["Average"],
                c=point_colors, s=80, edgecolors="white", linewidths=0.5)

    for _, row in df.iterrows():
        plt.annotate(
            row["Name"].split()[0],
            (row["Attendance"], row["Average"]),
            textcoords="offset points",
            xytext=(5, 5), fontsize=7, color="#444441"
        )

    plt.title("Attendance vs Academic Performance", fontsize=15, fontweight="bold", pad=15)
    plt.xlabel("Attendance (%)", fontsize=12)
    plt.ylabel("Average Marks", fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{CHARTS_DIR}/04_attendance_vs_performance.png", dpi=150)
    plt.close()

    print(f"4 charts saved to {CHARTS_DIR}/")


# ============================================================
# STEP 4: REPORT
# ============================================================

def generate_report(df, results):
    """Print and save the full analysis report."""

    r   = results  # shorthand
    now = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")

    lines = []

    def add(line=""):
        lines.append(line)

    add("=" * 60)
    add("       STUDENT PERFORMANCE ANALYZER — REPORT")
    add(f"       Generated on: {now}")
    add("=" * 60)

    add("\n[ CLASS OVERVIEW ]")
    add(f"  Total students analysed  : {len(df)}")
    add(f"  Class average (overall)  : {df['Average'].mean().round(2)}")
    add(f"  Pass rate (avg >= 50)    : {r['pass_rate']}%")
    add(f"  Good attendance rate     : {r['attend_rate']}%")

    add("\n[ SUBJECT-WISE AVERAGES ]")
    for subj, avg in r["subject_avgs"].items():
        add(f"  {subj:<12}: {avg}")
    add(f"  Strongest   : {r['strongest']}")
    add(f"  Weakest     : {r['weakest']}")

    add("\n[ TOP PERFORMERS ]")
    add(f"  Criteria : Average >= {TOP_AVG_THRESHOLD} AND Attendance >= {TOP_ATT_THRESHOLD}%")
    add(f"  Count    : {len(r['top_performers'])} students\n")
    for _, row in r["top_performers"].iterrows():
        add(f"  {row['Name']:<22} Avg: {row['Average']}   Attendance: {row['Attendance']}%")

    add("\n[ AT-RISK STUDENTS ]")
    add(f"  Criteria : Average < {RISK_AVG_THRESHOLD} OR Attendance < {RISK_ATT_THRESHOLD}%")
    add(f"  Count    : {len(r['at_risk'])} students\n")
    for _, row in r["at_risk"].iterrows():
        add(f"  {row['Name']:<22} Avg: {row['Average']}   Attendance: {row['Attendance']}%")

    add("\n[ ATTENDANCE IMPACT ]")
    add(f"  Avg marks (attendance >= {GOOD_ATTENDANCE}%) : {r['good_att_avg']}")
    add(f"  Avg marks (attendance <  {GOOD_ATTENDANCE}%) : {r['poor_att_avg']}")
    add(f"  Performance gap               : {r['att_gap']} marks")
    add(f"  Correlation coefficient       : {r['correlation']} ({r['corr_strength']})")

    add("\n[ INDIVIDUAL STUDENT SUMMARY ]")
    add(f"  {'Name':<22}{'Math':>6}{'Science':>9}{'English':>8}{'Avg':>7}{'Attend':>8}  {'Status'}")
    add("  " + "-" * 68)

    for _, row in df.sort_values("Average", ascending=False).iterrows():
        if row["Average"] >= TOP_AVG_THRESHOLD and row["Attendance"] >= TOP_ATT_THRESHOLD:
            status = "TOP"
        elif row["Average"] < RISK_AVG_THRESHOLD or row["Attendance"] < RISK_ATT_THRESHOLD:
            status = "AT-RISK"
        else:
            status = "Average"

        add(
            f"  {row['Name']:<22}{int(row['Math']):>6}{int(row['Science']):>9}"
            f"{int(row['English']):>8}{row['Average']:>7}{row['Attendance']:>7}%"
            f"  {status}"
        )

    add("\n[ RECOMMENDATIONS ]")
    add(f"  1. Schedule extra {r['weakest']} sessions — weakest subject class-wide.")
    add(f"  2. Contact {len(r['at_risk'])} at-risk students for counselling immediately.")
    add(f"  3. Introduce attendance incentives — correlation with marks is {r['correlation']}.")
    add(f"  4. Use top {len(r['top_performers'])} performers as peer mentors.")
    add(f"  5. Investigate root causes of low attendance in flagged students.")

    add("\n" + "=" * 60)
    add("  END OF REPORT")
    add("=" * 60)

    # Print to terminal
    for line in lines:
        print(line)

    # Save to file
    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines))

    print(f"\nReport saved to: {REPORT_PATH}")


# ============================================================
# MAIN — runs everything in order
# ============================================================

def main():
    print("Loading data...")
    df = load_data(DATA_PATH)

    print("Running analysis...")
    results = analyse(df)

    print("Creating charts...")
    create_charts(df, results)

    print("Generating report...")
    generate_report(df, results)

    print("\nDone! Your student analyzer ran successfully.")


# This ensures main() only runs when YOU run this file directly
# (not when another file imports it)
if __name__ == "__main__":
    main()