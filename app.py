import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# --- Configuration ---
FRED_API_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# IMPORTANT: Ensure your FRED_API_KEY is in your .streamlit/secrets.toml file.
# Example:
# FRED_API_KEY = "YOUR_ACTUAL_FRED_API_KEY_HERE"

# Define multiple FRED Series IDs and their display names
FRED_SERIES = {
    "Federal Funds Rate (DFF)": {
        "id": "DFF",
        "units": "Percent (%)",
        "frequency": "Daily",
        "description": "The Federal Funds Rate is a key interest rate in the U.S. economy, set by the Federal Reserve. It influences other interest rates.",
        "link": "https://fred.stlouisfed.org/series/DFF"
    },
    "Real GDP (GDPC1)": {
        "id": "GDPC1",
        "units": "Billions of Chained 2017 Dollars",
        "frequency": "Quarterly",
        "description": "Real Gross Domestic Product (GDP) is the value of the goods and services produced by an economy, adjusted for inflation.",
        "link": "https://fred.stlouisfed.org/series/GDPC1"
    },
    "Unemployment Rate (UNRATE)": {
        "id": "UNRATE",
        "units": "Percent (%)",
        "frequency": "Monthly",
        "description": "The Unemployment Rate represents the percentage of the labor force that is unemployed.",
        "link": "https://fred.stlouisfed.org/series/UNRATE"
    },
    "CPI (CPIAUCSL)": {
        "id": "CPIAUCSL",
        "units": "Index (1982-84=100)",
        "frequency": "Monthly",
        "description": "The Consumer Price Index (CPI) measures the average change over time in the prices paid by urban consumers for a market basket of consumer goods and services.",
        "link": "https://fred.stlouisfed.org/series/CPIAUCSL"
    },
    "10-Year Treasury Yield (DGS10)": {
        "id": "DGS10",
        "units": "Percent (%)",
        "frequency": "Daily",
        "description": "Market yield on U.S. Treasury securities at 10-year constant maturity.",
        "link": "https://fred.stlouisfed.org/series/DGS10"
    }
}

# --- Data Fetching Function ---
@st.cache_data(ttl=3600) # Cache data for 1 hour to avoid re-fetching
def fetch_fred_data(series_id):
    """
    Fetches economic data from the FRED API for a given series ID.
    Reads API key from Streamlit secrets.
    Returns a Pandas DataFrame.
    """
    try:
        api_key = st.secrets["FRED_API_KEY"]
    except KeyError:
        st.error("FRED API Key not found. Please add FRED_API_KEY to your .streamlit/secrets.toml file.")
        return pd.DataFrame()

    params = {
        "series_id": series_id,
        "file_type": "json",
        "api_key": api_key,
        "observation_start": "1950-01-01" # Fetch data from a sufficiently early date
    }
    
    try:
        response = requests.get(FRED_API_BASE_URL, params=params, timeout=15)
        response.raise_for_status() # Raise an exception for HTTP errors (like 400 Bad Request)
        data = response.json()

        if data and 'observations' in data:
            df = pd.DataFrame(data['observations'])
            
            # --- Data Cleaning & Preprocessing ---
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce') # 'coerce' turns '.' into NaN

            df.dropna(subset=['value'], inplace=True)
            df.set_index('date', inplace=True)
            
            return df
        else:
            st.error(f"No observations found for series ID: {series_id}. Check series ID or API key.")
            return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch data from FRED API: {e}. Ensure your FRED API key is valid and check your network connection.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return pd.DataFrame()

# --- Main Streamlit Application ---
def main():
    st.set_page_config(
        page_title="Public Data Visualizer Dashboard",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 Public Data Visualizer Dashboard")

    st.markdown("""
    Explore key economic indicators from the FRED (Federal Reserve Economic Data) API.
    Select a series from the sidebar to visualize its historical trend.
    """)

    # --- Sidebar Controls ---
    st.sidebar.header("Data Selection")

    # Selectbox for choosing the data series
    selected_series_name = st.sidebar.selectbox(
        "Choose an Economic Indicator:",
        options=list(FRED_SERIES.keys())
    )
    
    selected_series_info = FRED_SERIES[selected_series_name]
    selected_series_id = selected_series_info["id"]

    # --- Date Range Filter ---
    st.sidebar.subheader("Date Range")
    
    # Set default start date (e.g., 20 years ago)
    default_start_date = datetime(max(1950, datetime.now().year - 20), 1, 1).date()
    default_end_date = datetime.now().date()

    start_date = st.sidebar.date_input("Start Date:", value=default_start_date)
    end_date = st.sidebar.date_input("End Date:", value=default_end_date)

    if start_date > end_date:
        st.sidebar.error("Error: End Date cannot be before Start Date.")
        return # Stop execution if dates are invalid

    # --- Data Fetching and Display ---
    st.subheader(f"Historical Trend: {selected_series_name}")
    st.info(f"**Description:** {selected_series_info['description']}")
    st.info(f"**Frequency:** {selected_series_info['frequency']} | **Units:** {selected_series_info['units']}")
    st.markdown(f"**Source:** [FRED - {selected_series_name}]({selected_series_info['link']})")


    with st.spinner(f"Fetching data for {selected_series_name} from FRED..."):
        df = fetch_fred_data(selected_series_id)

    if not df.empty:
        # Filter DataFrame by selected date range
        df_filtered = df.loc[start_date.isoformat():end_date.isoformat()]

        if df_filtered.empty:
            st.warning("No data available for the selected date range. Please adjust your dates.")
        else:
            st.success(f"Data for {selected_series_name} fetched and filtered successfully!")
            
            # --- Plotly Visualization (Line Chart) ---
            fig = px.line(
                df_filtered,
                x=df_filtered.index, # Date is the index
                y='value',
                title=f'{selected_series_name} Over Time',
                labels={'date': 'Date', 'value': selected_series_info['units']},
                line_shape='linear' # 'linear' or 'hv' for step-like data
            )
            
            # Customize layout for better readability and interactivity
            fig.update_layout(
                hovermode="x unified", # Shows all values on a single x-coordinate hover
                title_x=0.5, # Center title
                xaxis_title="Date",
                yaxis_title=f"{selected_series_info['units']}",
                template="plotly_white", # Clean background
                height=500 # Set a fixed height
            )
            
            # Add date range selectors to the x-axis for quick navigation
            fig.update_xaxes(
                rangeselector_buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=5, label="5y", step="year", stepmode="backward"),
                    dict(step="all")
                ]),
                rangeslider_visible=True, # Show the range slider at the bottom
                # type="date" # Ensure x-axis is treated as date
            )
            
            st.plotly_chart(fig, use_container_width=True)

            # Optional: Display raw data preview (collapsible)
            with st.expander("View Raw Data Preview"):
                st.dataframe(df_filtered.head())
                st.write(f"Showing {len(df_filtered)} data points.")


    else:
        st.warning(f"Could not load data for {selected_series_name}. Please ensure your FRED API key is correctly set in .streamlit/secrets.toml and try again.")

if __name__ == "__main__":
    main()