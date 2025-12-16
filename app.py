import streamlit as st
import pandas as pd
import os

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Financial Text Analyzer",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# Paths
# --------------------------------------------------
CSV_PATH = "output/csv/rich_dad_analysis_output.csv"
CHART_PATH = "output/charts"

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown(
    """
    <h1 style="text-align:center;">📘 Financial Text Analyzer</h1>
    <p style="text-align:center; color:gray;">
    Chapter-wise Financial Insight Analysis<br>
    <b>Book:</b> Rich Dad Poor Dad – Robert Kiyosaki
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# Load Data
# --------------------------------------------------
if not os.path.exists(CSV_PATH):
    st.error("CSV file not found. Please run backend analysis first.")
    st.stop()

df = pd.read_csv(CSV_PATH)

# --------------------------------------------------
# Sidebar Filters
# --------------------------------------------------
st.sidebar.header("🔍 Filters")

category_filter = st.sidebar.multiselect(
    "Select Financial Categories",
    options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)

chapter_filter = st.sidebar.multiselect(
    "Select Chapters",
    options=sorted(df["Chapter"].unique()),
    default=sorted(df["Chapter"].unique())
)

filtered_df = df[
    (df["Category"].isin(category_filter)) &
    (df["Chapter"].isin(chapter_filter))
]

# --------------------------------------------------
# KPI Metrics
# --------------------------------------------------
st.subheader("📌 Overview")

col1, col2, col3 = st.columns(3)

col1.metric("📄 Total Sentences", len(filtered_df))
col2.metric("📊 Total Financial Score", int(filtered_df["Score"].sum()))
col3.metric("📚 Chapters Covered", filtered_df["Chapter"].nunique())

st.markdown("---")

# --------------------------------------------------
# Tabs Layout
# --------------------------------------------------
tab1, tab2, tab3 = st.tabs(
    ["📊 Charts Dashboard", "📄 Extracted Sentences", "⬇ Download"]
)

# --------------------------------------------------
# TAB 1: Charts
# --------------------------------------------------
with tab1:
    st.subheader("📊 Financial Insights Dashboard")

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    with c1:
        st.markdown("### Category-wise Score (Bar Chart)")
        st.image(os.path.join(CHART_PATH, "category_scores_bar.png"), use_container_width=True)

    with c2:
        st.markdown("### Financial Theme Distribution (Pie Chart)")
        st.image(os.path.join(CHART_PATH, "category_distribution_pie.png"), use_container_width=True)

    with c3:
        st.markdown("### Chapter-wise Financial Trend (Line Chart)")
        st.image(os.path.join(CHART_PATH, "chapter_trend_line.png"), use_container_width=True)

    with c4:
        st.markdown("### Financial Keyword Frequency")
        st.image(os.path.join(CHART_PATH, "financial_keyword_frequency.png"), use_container_width=True)

# --------------------------------------------------
# TAB 2: Data Table
# --------------------------------------------------
with tab2:
    st.subheader("📄 Extracted Financial & Motivational Sentences")
    st.caption("Filtered by selected categories and chapters")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=450
    )

# --------------------------------------------------
# TAB 3: Download
# --------------------------------------------------
with tab3:
    st.subheader("⬇ Download Analysis Data")

    st.download_button(
        label="Download Filtered CSV",
        data=filtered_df.to_csv(index=False),
        file_name="financial_text_analysis_filtered.csv",
        mime="text/csv"
    )

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown(
    """
    <hr>
    <p style="text-align:center; color:gray;">
    Developed by Sandhya Wani | Financial Text Analyzer Project
    </p>
    """,
    unsafe_allow_html=True
)
