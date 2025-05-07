import streamlit as st

# Sidebar options
st.sidebar.title("Navigation")
topic = st.sidebar.radio("Select Topic", ["Overview", "Data Warehouse Architecture", "Enterprise Data Management"])

st.title("Data Warehousing & Enterprise Data Management")

# Use tabs for major categories
tab1, tab2 = st.tabs(["Core Concepts", "Advanced Topics"])

# Overview Section
if topic == "Overview":
    with tab1:
        st.header("Core Concepts")
        with st.expander("What is Data Warehousing?"):
            st.write("Data Warehousing is a system used for reporting and data analysis, acting as a central repository for integrated data.")
        with st.expander("What is Enterprise Data Management?"):
            st.write("Enterprise Data Management (EDM) is a framework that helps ensure high data quality and effective data governance.")

# Data Warehouse Architecture Section
elif topic == "Data Warehouse Architecture":
    with tab1:
        st.header("Data Warehouse Architecture")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Staging Area")
            st.write("Temporarily holds raw data before processing.")
        with col2:
            st.subheader("Data Integration")
            st.write("Combines data from multiple sources using ETL/ELT.")

        with st.expander("More on Architecture"):
            st.write("""
            - **Data Sources**: Internal and external systems.
            - **Staging Area**: Prepares data for integration.
            - **Warehouse Layer**: Central storage.
            - **Data Marts**: Subsets for specific departments.
            """)

# EDM Section
elif topic == "Enterprise Data Management":
    with tab2:
        st.header("EDM Components")
        st.write("Effective EDM consists of several pillars:")
        with st.expander("Key Pillars of EDM"):
            st.write("""
            - Data Governance
            - Master Data Management
            - Data Stewardship
            - Metadata Management
            - Data Quality
            """)

        st.markdown("#### Why EDM Matters")
        st.write("It ensures that data is accurate, secure, and accessible to the right users.")

# Footer info
st.markdown("---")
st.caption("Streamlit App Example – Data Warehousing & EDM")
