import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(layout="wide", page_title="Data Profiling & Quality Audit")

st.title("Data Profiling and Data Quality Analysis")
st.markdown("This dashboard fulfills the quality audit requirements for the Road Safety (BAAC) dataset across the entire relational model (4 tables).")

# ==========================================
# 1. DATA LOADING (The 4 Bronze tables)
# ==========================================
@st.cache_data
def load_all_data():
    files = {
        "Characteristics": "bronze_caract.csv",
        "Locations": "bronze_lieux.csv",
        "Vehicles": "bronze_vehicules.csv",
        "Users": "bronze_usagers.csv"
    }
    dataframes = {}
    for name, file_path in files.items():
        try:
            # Loading data, ignoring memory warnings for mixed types
            dataframes[name] = pd.read_csv(file_path, sep=';', low_memory=False)
        except FileNotFoundError:
            st.error(f"⚠️ File {file_path} not found. Please ensure it is in the same directory.")
            dataframes[name] = pd.DataFrame() # Fallback to empty dataframe
    return dataframes

db = load_all_data()

# ==========================================
# 2. NAVIGATION SIDEBAR
# ==========================================
st.sidebar.header("Guided Questions")
page = st.sidebar.radio("Go to section:", [
    "A. Dataset Structure", 
    "B. Missing Values & Completeness", 
    "C. Consistency & Validity Checks", 
    "D. Data Quality Summary"
])

# ==========================================
# PART A : DATASET STRUCTURE
# ==========================================
if page == "A. Dataset Structure":
    st.header("A. Dataset Structure")
    
    # Selector to explore the 4 tables without cluttering the screen
    selected_table = st.selectbox("Select the table to explore:", list(db.keys()))
    df_selected = db[selected_table]
    
    if not df_selected.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Column Inventory ({selected_table})")
            types_df = pd.DataFrame(df_selected.dtypes, columns=['Data Type']).reset_index()
            types_df = types_df.rename(columns={'index': 'Column Name'})
            st.dataframe(types_df, use_container_width=True, height=400)

        with col2:
            st.subheader("Semantic Meaning & Keys")
            if selected_table == "Characteristics":
                st.write("**Primary Key:** `Num_Acc`")
                st.write("Contains accident metadata: Date (`jour`, `mois`, `an`, `hrmn`), GPS Location (`lat`, `long`), and global conditions (`lum`, `atm`, `col`).")
            elif selected_table == "Locations":
                st.write("**Primary/Foreign Key:** `Num_Acc`")
                st.write("Describes the road infrastructure at the time of the accident: Road category (`catr`), Maximum speed limit (`vma`), Surface condition (`surf`).")
            elif selected_table == "Vehicles":
                st.write("**Composite Key:** `Num_Acc` + `num_veh`")
                st.write("Details the vehicles involved: Category (`catv`), Motorization type (`motor`), Initial point of impact (`choc`).")
            elif selected_table == "Users":
                st.write("**Composite Key:** `Num_Acc` + `num_veh` + `num_usager` (implicit)")
                st.write("Details the people involved: Injury severity (`grav`), Birth year (`an_nais`), Gender (`sexe`), Reason for travel (`trajet`).")

# ==========================================
# PART B : MISSING VALUES & COMPLETENESS
# ==========================================
elif page == "B. Missing Values & Completeness":
    st.header("B. Missing Values and Completeness")
    st.markdown("Analysis of missing values (NaN) across all tables in the dataset.")
    
    # Using tabs to separate the missing value charts per table
    tabs = st.tabs(list(db.keys()))
    
    for i, (table_name, df) in enumerate(db.items()):
        with tabs[i]:
            if not df.empty:
                missing_percentages = (df.isnull().sum() / len(df)) * 100
                missing_df = missing_percentages.reset_index()
                missing_df.columns = ['Column', 'Missing Percentage']
                missing_df = missing_df[missing_df['Missing Percentage'] > 0].sort_values(by='Missing Percentage', ascending=False)
                
                if not missing_df.empty:
                    fig = px.bar(missing_df, x='Column', y='Missing Percentage', 
                                 title=f"% of missing values - {table_name}",
                                 text_auto='.2f', color='Missing Percentage', color_continuous_scale='Reds')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.success(f"No missing values detected in the {table_name} table.")
                    
    st.markdown("---")
    st.subheader("Critical Missingness & Remediation Strategies")
    st.error("**Critical Issue: `lat` and `long` (Characteristics)**\nAbout 5% of accidents lack geographic coordinates. This prevents any spatial analysis or hotspot detection. **Action (Silver layer):** Drop rows without geolocation.")
    st.warning("**Technical Issue: `place` and `trajet` (Users)**\nHigh rate of missing values. **Action (Silver layer):** Replace with default value `-1` (Not Provided) to preserve user records without breaking the schema.")

# ==========================================
# PART C : CONSISTENCY & VALIDITY CHECKS
# ==========================================
elif page == "C. Consistency & Validity Checks":
    st.header("C. Consistency and Validity Checks")
    
    st.subheader("1. Duplicates Detection (Across all tables)")
    cols = st.columns(4)
    for i, (name, df) in enumerate(db.items()):
        if not df.empty:
            cols[i].metric(label=f"Duplicates ({name})", value=df.duplicated().sum())

    st.markdown("---")
    st.subheader("2. Value Ranges & Anomalies (Outliers)")
    
    # 4 charts for 4 specific anomalies across the 4 tables
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown("**1. Characteristics: Geographic Noise**")
        if not db["Characteristics"].empty:
            fig_map = px.scatter(db["Characteristics"], x='long', y='lat', title="GPS Dispersion (Outliers > 90)")
            st.plotly_chart(fig_map, use_container_width=True)
            
    with row1_col2:
        st.markdown("**2. Locations: Impossible Speeds (`vma`)**")
        if not db["Locations"].empty and 'vma' in db["Locations"].columns:
            # Filter for visualization to make the chart readable
            vma_df = db["Locations"][db["Locations"]['vma'] > -2]
            fig_vma = px.histogram(vma_df, x='vma', title="Speed Limit Distribution (Anomalies > 130 km/h)", nbins=50)
            st.plotly_chart(fig_vma, use_container_width=True)

    with row2_col1:
        st.markdown("**3. Users: Incorrect Birth Years**")
        if not db["Users"].empty and 'an_nais' in db["Users"].columns:
            fig_age = px.histogram(db["Users"], x='an_nais', title="Birth Year Distribution (Future dates or < 1900)")
            st.plotly_chart(fig_age, use_container_width=True)

    with row2_col2:
        st.markdown("**4. Vehicles: Technical Placeholders**")
        if not db["Vehicles"].empty and 'motor' in db["Vehicles"].columns:
            motor_counts = db["Vehicles"]['motor'].value_counts().reset_index()
            motor_counts.columns = ['Motorization Code', 'Count']
            fig_motor = px.bar(motor_counts, x='Motorization Code', y='Count', title="Massive presence of code '-1' (Unknown)")
            st.plotly_chart(fig_motor, use_container_width=True)

# ==========================================
# PART D : DATA QUALITY SUMMARY
# ==========================================
elif page == "D. Data Quality Summary":
    st.header("D. Data Quality Summary")
    
    st.subheader("Global Quality Report")
    st.info("""
    **Summary of the relational audit:**
    * **Characteristics:** Decimal separator formatting issues (commas instead of dots) and aberrant GPS coordinates.
    * **Locations:** Aberrant maximum authorized speeds (VMA) (e.g., 500 km/h) requiring data capping.
    * **Vehicles:** Very high proportion of technical codes (`-1`, `0`) indicating missing motorization information.
    * **Users:** Data entry errors on birth years and high non-response rate for the reason of travel.
    """)
    
    st.subheader("Impact Analysis on Star Schema (Gold Layer)")
    st.error("""
    **Consequences on BI analytics if left untreated:**
    1. **Broken Referential Integrity:** If duplicates are not removed in `Vehicles` or `Users`, the join (Merge) with the fact table will create a Cartesian product, artificially multiplying the number of accidents.
    2. **Distorted Filters:** A Power BI user filtering for "Accidents at 50 km/h" will get incorrect results due to `-1` or `0` entries.
    3. **Impossible Demographic Calculations:** The age pyramid will collapse due to birth years entered as `2027` or `1890`.
    """)
    
    st.success("**Conclusion:** The Medallion architecture approach is essential. The Silver layer will allow purging these 4 tables in a synchronized manner before assembling them in the clean, analytical Gold layer.")