import streamlit as st
import pandas as pd
import os

# Page configuration
st.set_page_config(
    page_title="Financial Text Analyzer",
    layout="wide"
)

# Define base directory and file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "output", "csv", "rich_dad_analysis_output.csv")
CHART_PATH = os.path.join(BASE_DIR, "output", "charts")

# Function to safely display chart images
def show_image(filename, title):
    path = os.path.join(CHART_PATH, filename)
    st.markdown(f"### {title}")
    if os.path.exists(path):
        st.image(path, use_container_width=True)
    else:
        st.warning(f"Chart not found: {filename}")

# Application header
st.markdown(
    """
    <h1 style="text-align:center;">Financial Text Analyzer</h1>
    <p style="text-align:center; color:gray;">
        Chapter-wise Financial Insight Analysis<br>
        <b>Book:</b> Rich Dad Poor Dad – Robert Kiyosaki
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# Load CSV data
if not os.path.exists(CSV_PATH):
    st.error("CSV file not found. Please run the backend analysis first.")
    st.stop()

df = pd.read_csv(CSV_PATH)

# Sidebar filters
st.sidebar.header("Filters")

category_filter = st.sidebar.multiselect(
    "Select financial categories",
    options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)

chapter_filter = st.sidebar.multiselect(
    "Select chapters",
    options=sorted(df["Chapter"].unique()),
    default=sorted(df["Chapter"].unique())
)

filtered_df = df[
    (df["Category"].isin(category_filter)) &
    (df["Chapter"].isin(chapter_filter))
]

# Overview metrics
st.subheader("Overview")

col1, col2, col3 = st.columns(3)
col1.metric("Total sentences", len(filtered_df))
col2.metric("Total financial score", int(filtered_df["Score"].sum()))
col3.metric("Chapters covered", filtered_df["Chapter"].nunique())

st.markdown("---")

# Tabs for charts, table, and download
tab1, tab2, tab3 = st.tabs(
    ["Charts Dashboard", "Extracted Sentences", "Download"]
)

# Charts dashboard
with tab1:
    st.subheader("Financial Insights Dashboard")

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    with c1:
        show_image("category_score_bar.png", "Category-wise Financial Score")

    with c2:
        show_image("category_distribution_pie.png", "Financial Theme Distribution")

    with c3:
        show_image("chapter_trend_line.png", "Chapter-wise Financial Trend")

    with c4:
        show_image("financial_keyword_frequency.png", "Financial Keyword Frequency")

# Display extracted sentences
with tab2:
    st.subheader("Extracted Financial and Motivational Sentences")
    st.caption("Filtered by selected categories and chapters")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=450
    )

# Download filtered data
with tab3:
    st.subheader("Download Analysis Data")

    st.download_button(
        label="Download filtered CSV",
        data=filtered_df.to_csv(index=False),
        file_name="financial_text_analysis_filtered.csv",
        mime="text/csv"
    )


