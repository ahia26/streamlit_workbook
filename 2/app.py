import streamlit as st
import pandas as pd

st.title("CSV Data Viewer")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file is not None:
    # Load CSV with pandas
    df = pd.read_csv(uploaded_file)

    # Show raw data with checkbox
    if st.checkbox("Show raw data"):
        st.dataframe(df)

    # Selectbox to filter by a column (e.g., 'Category')
    column_to_filter = st.selectbox("Select a column to filter", df.columns)

    # If the column has many unique values, filter by them
    if df[column_to_filter].nunique() > 0:
        unique_values = df[column_to_filter].unique()
        selected_value = st.selectbox(f"Filter by value in '{column_to_filter}'", unique_values)
        filtered_df = df[df[column_to_filter] == selected_value]
        st.write(f"Filtered data by {column_to_filter} = {selected_value}:")
        st.dataframe(filtered_df)
