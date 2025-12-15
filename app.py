import streamlit as st
import pandas as pd
import os

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Financial Text Analyzer",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# Header Section
# --------------------------------------------------
st.markdown(
    """
    <h1 style='text-align: center;'>📘 Financial Text Analyzer</h1>
    <p style='text-align: center; color: gray;'>
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
csv_path = "output/csv/rich_dad_analysis_output.csv"

if not os.path.exists(csv_path):
    st.error("❌ CSV file not found. Please run the backend script first.")
    st.stop()

df = pd.read_csv(csv_path)

# --------------------------------------------------
# Sidebar (Filters)
# --------------------------------------------------
st.sidebar.markdown("## 🔍 Filters")

selected_categories = st.sidebar.multiselect(
    "Financial Categories",
    options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)

selected_chapters = st.sidebar.multiselect(
    "Chapters",
    options=sorted(df["Chapter"].unique()),
    default=sorted(df["Chapter"].unique())
)

filtered_df = df[
    (df["Category"].isin(selected_categories)) &
    (df["Chapter"].isin(selected_chapters))
]

# --------------------------------------------------
# Dashboard Metrics
# --------------------------------------------------
st.markdown("## 📌 Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
    label="📄 Total Sentences",
    value=len(filtered_df)
)

col2.metric(
    label="📊 Total Financial Score",
    value=int(filtered_df["Score"].sum())
)

col3.metric(
    label="📚 Chapters Covered",
    value=filtered_df["Chapter"].nunique()
)

st.markdown("<br>", unsafe_allow_html=True)

# --------------------------------------------------
# Charts Section
# --------------------------------------------------
st.markdown("## 📊 Financial Insights")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("### Category-wise Financial Score")
    category_scores = (
        filtered_df.groupby("Category")["Score"]
        .sum()
        .sort_values()
    )
    st.bar_chart(category_scores)

with chart_col2:
    st.markdown("### Chapter-wise Financial Trend")
    chapter_scores = (
        filtered_df.groupby("Chapter")["Score"]
        .sum()
        .sort_index()
    )
    st.line_chart(chapter_scores)

st.markdown("<hr>", unsafe_allow_html=True)

# --------------------------------------------------
# Data Table Section
# --------------------------------------------------
st.markdown("## 📄 Extracted Financial Sentences")
st.caption("Filtered results based on selected categories and chapters")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=400
)

# --------------------------------------------------
# Download Section
# --------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)

st.download_button(
    label="⬇ Download Filtered Data (CSV)",
    data=filtered_df.to_csv(index=False),
    file_name="financial_text_analysis.csv",
    mime="text/csv"
)
