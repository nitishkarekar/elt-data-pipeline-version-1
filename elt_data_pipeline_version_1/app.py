import streamlit as st
import duckdb
import pandas as pd
import altair as alt

# 1. Page Configuration
st.set_page_config(
    page_title="EV Analytics Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚡ Electric Vehicle Insights")
st.markdown("Real-time analysis of EV data pipeline: **Google Cloud** → **dbt** → **MotherDuck**")

# 2. Connect to Database
# We use st.cache_resource so we don't reconnect every time you click a button
@st.cache_resource
def get_connection():
    token = st.secrets["MOTHERDUCK_TOKEN"]
    return duckdb.connect(f'md:?motherduck_token={token}')

conn = get_connection()

# 3. Load Data
# We select only the columns we need to keep it fast
query = """
    SELECT 
        make, 
        model, 
        model_year, 
        ev_type, 
        electric_range, 
        city, 
        state 
    FROM test_data
"""
df = conn.sql(query).df()

# 4. Top Key Metrics (The "Scoreboard")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Vehicles", f"{len(df):,}")

with col2:
    # Handle cases where range might be 0 or null
    avg_range = df[df['electric_range'] > 0]['electric_range'].mean()
    st.metric("Avg Electric Range", f"{int(avg_range)} miles")

with col3:
    top_make = df['make'].mode()[0]
    st.metric("Top Manufacturer", top_make)

with col4:
    # Most common EV type (BEV vs PHEV)
    top_type = df['ev_type'].mode()[0]
    st.metric("Dominant EV Type", top_type)

st.divider()

# 5. Visualizations
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🚗 Market Share by Manufacturer")
    # Get top 10 makes
    top_makes = df['make'].value_counts().head(10).reset_index()
    top_makes.columns = ['Make', 'Count']
    
    # Simple Bar Chart
    st.bar_chart(top_makes.set_index('Make'))

with col_right:
    st.subheader("📈 Adoption Trend (Model Year)")
    # Group by year
    trend = df.groupby('model_year').size().reset_index(name='Vehicles')
    # Filter out weird future years or very old data if necessary
    trend = trend[trend['model_year'] > 2010] 
    
    # Area Chart for trend
    st.area_chart(trend.set_index('model_year'))

# 6. Detailed Breakdown
st.subheader("🔍 Detailed View")
col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    selected_make = st.selectbox("Filter by Make:", ["All"] + list(df['make'].unique()))

with col_filter2:
    selected_year = st.selectbox("Filter by Year:", ["All"] + sorted(list(df['model_year'].unique()), reverse=True))

# Apply Filters
filtered_df = df.copy()
if selected_make != "All":
    filtered_df = filtered_df[filtered_df['make'] == selected_make]
if selected_year != "All":
    filtered_df = filtered_df[filtered_df['model_year'] == selected_year]

st.dataframe(
    filtered_df[['model_year', 'make', 'model', 'ev_type', 'electric_range', 'city']],
    use_container_width=True,
    hide_index=True
)