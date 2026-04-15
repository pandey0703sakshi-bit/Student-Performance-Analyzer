# ============================================================
# STUDENT PERFORMANCE ANALYZER — STREAMLIT DASHBOARD
# Run with: streamlit run dashboard.py
# ============================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os
import datetime

# ============================================================
# PAGE CONFIGURATION — must be the very first Streamlit call
# ============================================================

st.set_page_config(
    page_title="Student Performance Analyzer",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# CONFIGURATION
# ============================================================

TOP_AVG         = 80
TOP_ATT         = 85
RISK_AVG        = 50
RISK_ATT        = 65
GOOD_ATTENDANCE = 75

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_status(row):
    if row["Average"] >= TOP_AVG and row["Attendance"] >= TOP_ATT:
        return "Top Performer"
    elif row["Average"] < RISK_AVG or row["Attendance"] < RISK_ATT:
        return "At-Risk"
    else:
        return "Average"


def load_data(file):
    """Load CSV or Excel from an uploaded file object."""
    name = file.name

    if name.endswith(".csv"):
        df = pd.read_csv(file)

    elif name.endswith(".xlsx") or name.endswith(".xls"):
        # Try reading normally first
        df = pd.read_excel(file)

        # If first column looks like a report title (not "Name"), skip rows
        # and search for the real header row
        if "Name" not in df.columns and "name" not in [c.lower() for c in df.columns]:
            for skip in range(1, 10):
                file.seek(0)
                test = pd.read_excel(file, skiprows=skip)
                test.columns = test.columns.str.strip()
                if "Name" in test.columns:
                    df = test
                    break

    else:
        return None, "Unsupported file format. Please upload a CSV or Excel file."

    # Strip accidental spaces from column names
    df.columns = df.columns.str.strip()

    # Check all required columns exist
    required = ["Name", "Math", "Science", "English", "Attendance"]
    missing  = [col for col in required if col not in df.columns]

    if missing:
        found   = list(df.columns)
        message = (
            f"Missing columns: **{', '.join(missing)}**\n\n"
            f"Your file has: `{', '.join(found)}`\n\n"
            f"Required columns: `Name, Math, Science, English, Attendance`\n\n"
            "Check for typos, extra spaces, or different capitalisation."
        )
        return None, message

    # Convert mark columns to numbers in case they loaded as text
    for col in ["Math", "Science", "English", "Attendance"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Average"] = df[["Math", "Science", "English"]].mean(axis=1).round(2)
    df["Status"]  = df.apply(get_status, axis=1)
    return df, None


def load_default():
    """Load the local students.csv as fallback."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "data", "students.csv")
    df = pd.read_csv(csv_path)
    df["Average"] = df[["Math", "Science", "English"]].mean(axis=1).round(2)
    df["Status"]  = df.apply(get_status, axis=1)
    return df


# ============================================================
# SIDEBAR — file upload + filters
# ============================================================

with st.sidebar:
    st.title("Controls")
    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Upload your own dataset",
        type=["csv", "xlsx"],
        help="File must have columns: Name, Math, Science, English, Attendance"
    )

    st.markdown("---")
    st.subheader("Filter Students")

    min_att, max_att = st.slider(
        "Attendance range (%)",
        min_value=0, max_value=100,
        value=(0, 100)
    )

    show_top  = st.checkbox("Show Top Performers", value=True)
    show_avg  = st.checkbox("Show Average",        value=True)
    show_risk = st.checkbox("Show At-Risk",        value=True)

    st.markdown("---")
    st.caption("Student Performance Analyzer")


# ============================================================
# LOAD DATA
# ============================================================

if uploaded_file:
    df, error = load_data(uploaded_file)
    if error:
        st.error(error)
        st.info("Falling back to default dataset while you fix your file.")
        df = load_default()
    else:
        st.sidebar.success(f"Loaded: {uploaded_file.name}")
else:
    df = load_default()
    st.sidebar.info("Using default dataset (students.csv)")


# ============================================================
# APPLY FILTERS
# ============================================================

df_filtered = df[
    (df["Attendance"] >= min_att) &
    (df["Attendance"] <= max_att)
]

allowed_statuses = []
if show_top:  allowed_statuses.append("Top Performer")
if show_avg:  allowed_statuses.append("Average")
if show_risk: allowed_statuses.append("At-Risk")

df_filtered = df_filtered[df_filtered["Status"].isin(allowed_statuses)]


# ============================================================
# MAIN PAGE
# ============================================================

st.title("Student Performance Analyzer")
st.markdown(
    "Upload any student dataset or use the default one. "
    "Use the sidebar to filter by attendance or student status."
)
st.markdown("---")


# ============================================================
# SECTION 1: METRIC CARDS
# ============================================================

total       = len(df_filtered)
class_avg   = df_filtered["Average"].mean().round(2) if total > 0 else 0
top_count   = len(df_filtered[df_filtered["Status"] == "Top Performer"])
risk_count  = len(df_filtered[df_filtered["Status"] == "At-Risk"])
pass_rate   = round(len(df_filtered[df_filtered["Average"] >= RISK_AVG]) / total * 100, 1) if total > 0 else 0
correlation = df_filtered["Attendance"].corr(df_filtered["Average"]).round(2) if total > 0 else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Students",      total)
col2.metric("Class Average",       class_avg)
col3.metric("Pass Rate",           f"{pass_rate}%")
col4.metric("Top Performers",      top_count)
col5.metric("At-Risk Students",    risk_count)
col6.metric("Attend. Correlation", correlation)

st.markdown("---")


# ============================================================
# SECTION 2: CHARTS
# ============================================================

st.subheader("Performance Visualizations")

chart_col1, chart_col2 = st.columns(2)

# Chart 1: Subject averages bar chart
with chart_col1:
    st.markdown("**Subject-wise class averages**")

    subject_avgs = {
        "Math"    : df_filtered["Math"].mean().round(2),
        "Science" : df_filtered["Science"].mean().round(2),
        "English" : df_filtered["English"].mean().round(2),
    }

    fig1, ax1 = plt.subplots(figsize=(5, 3.5))
    bars = ax1.bar(
        subject_avgs.keys(),
        subject_avgs.values(),
        color=["#378ADD", "#1D9E75", "#E24B4A"],
        width=0.5, edgecolor="white"
    )

    for bar, val in zip(bars, subject_avgs.values()):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            str(val),
            ha="center", va="bottom", fontsize=10, fontweight="bold"
        )

    ax1.set_ylim(0, 100)
    ax1.set_ylabel("Average Marks")
    ax1.set_xlabel("Subject")
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close()

# Chart 2: Score distribution histogram
with chart_col2:
    st.markdown("**Distribution of student averages**")

    fig2, ax2 = plt.subplots(figsize=(5, 3.5))
    ax2.hist(df_filtered["Average"], bins=10,
             color="#7F77DD", edgecolor="white", linewidth=0.8)
    ax2.axvline(x=RISK_AVG, color="#E24B4A", linestyle="--",
                linewidth=1.5, label=f"At-risk ({RISK_AVG})")
    ax2.axvline(x=TOP_AVG, color="#1D9E75", linestyle="--",
                linewidth=1.5, label=f"Top ({TOP_AVG})")

    if total > 0:
        ax2.axvline(df_filtered["Average"].mean(), color="orange",
                    linestyle="-", linewidth=2,
                    label=f"Mean ({df_filtered['Average'].mean().round(1)})")

    ax2.set_xlabel("Average Marks")
    ax2.set_ylabel("Number of Students")
    ax2.legend(fontsize=8)
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

st.markdown("---")

# Charts 3 & 4: Heatmap + Scatter
st.subheader("Deep Dive Charts")

heat_col, scatter_col = st.columns(2)

with heat_col:
    st.markdown("**Performance heatmap**")

    if total > 0:
        heatmap_data = df_filtered.set_index("Name")[["Math", "Science", "English"]]
        fig3, ax3 = plt.subplots(figsize=(5, max(4, total * 0.3)))
        sns.heatmap(
            heatmap_data,
            annot=True, fmt="d",
            cmap="RdYlGn",
            linewidths=0.5, linecolor="white",
            vmin=0, vmax=100,
            ax=ax3
        )
        ax3.set_xlabel("Subject")
        ax3.set_ylabel("")
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()
    else:
        st.info("No students match current filters.")

with scatter_col:
    st.markdown("**Attendance vs performance**")

    if total > 0:
        point_colors = df_filtered["Status"].map({
            "Top Performer" : "#1D9E75",
            "Average"       : "#378ADD",
            "At-Risk"       : "#E24B4A"
        })

        fig4, ax4 = plt.subplots(figsize=(5, 4))
        ax4.scatter(
            df_filtered["Attendance"],
            df_filtered["Average"],
            c=point_colors, s=80,
            edgecolors="white", linewidths=0.5
        )

        for _, row in df_filtered.iterrows():
            ax4.annotate(
                row["Name"].split()[0],
                (row["Attendance"], row["Average"]),
                textcoords="offset points",
                xytext=(5, 5), fontsize=7, color="#444441"
            )

        ax4.set_xlabel("Attendance (%)")
        ax4.set_ylabel("Average Marks")
        sns.despine()
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close()
    else:
        st.info("No students match current filters.")

st.markdown("---")


# ============================================================
# SECTION 3: STUDENT DATA TABLE
# ============================================================

st.subheader("Student Data Table")

def highlight_status(val):
    if val == "Top Performer":
        return "background-color: #E1F5EE; color: #0F6E56; font-weight: bold"
    elif val == "At-Risk":
        return "background-color: #FCEBEB; color: #A32D2D; font-weight: bold"
    else:
        return "background-color: #E6F1FB; color: #185FA5"

display_df = df_filtered.sort_values("Average", ascending=False).reset_index(drop=True)
display_df.index += 1

# FIX: .map() replaces deprecated .applymap() in Pandas 2.x
styled_df = display_df.style.map(highlight_status, subset=["Status"])

st.dataframe(styled_df, use_container_width=True, height=400)

st.markdown("---")


# ============================================================
# SECTION 4: AT-RISK DETAILS + RECOMMENDATIONS
# ============================================================

risk_col, rec_col = st.columns(2)

with risk_col:
    st.subheader("At-Risk Students")
    at_risk_df = df_filtered[df_filtered["Status"] == "At-Risk"][
        ["Name", "Average", "Attendance"]
    ].sort_values("Average")

    if len(at_risk_df) > 0:
        for _, row in at_risk_df.iterrows():
            st.error(
                f"**{row['Name']}** — "
                f"Avg: {row['Average']} | "
                f"Attendance: {row['Attendance']}%"
            )
    else:
        st.success("No at-risk students in current filter.")

with rec_col:
    st.subheader("Recommendations")

    weakest   = min(subject_avgs, key=subject_avgs.get)
    strongest = max(subject_avgs, key=subject_avgs.get)

    st.warning(f"Schedule extra **{weakest}** sessions — weakest subject.")
    st.info(f"**{strongest}** is the strongest subject — maintain momentum.")

    if risk_count > 0:
        st.error(f"Contact **{risk_count} at-risk** students for counselling.")

    if correlation >= 0.7:
        st.success(
            f"Attendance correlation is **{correlation}** — "
            "strong link with marks. Incentivise attendance."
        )

    st.info("Use top performers as peer mentors for struggling students.")

st.markdown("---")


# ============================================================
# SECTION 5: DOWNLOAD BUTTONS
# ============================================================

st.subheader("Download Results")

dl_col1, dl_col2 = st.columns(2)

with dl_col1:
    csv_data = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered data as CSV",
        data=csv_data,
        file_name="filtered_students.csv",
        mime="text/csv"
    )

with dl_col2:
    if len(at_risk_df) > 0:
        risk_csv = at_risk_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download at-risk list as CSV",
            data=risk_csv,
            file_name="at_risk_students.csv",
            mime="text/csv"
        )
    else:
        st.write("No at-risk students to download.")