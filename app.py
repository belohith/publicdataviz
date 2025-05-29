import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json # You might need this if FRED returns JSON, though requests usually handles it.

# --- Configuration ---
# FRED API Key (retrieved securely via Streamlit secrets)
FRED_API_KEY = st.secrets["FRED_API_KEY"]
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Define the economic indicators you want to display
# Key is the user-friendly name, value is a dictionary with FRED Series ID and description
ECONOMIC_INDICATORS = {
    "Federal Funds Rate": {
        "id": "DFF",
        "description": "The effective federal funds rate, representing the target interest rate set by the Federal Open Market Committee (FOMC)."
    },
    "Real Gross Domestic Product (GDP)": {
        "id": "GDPC1",
        "description": "Real GDP, measuring the value of goods and services produced in the U.S. in constant dollars, adjusted for inflation."
    },
    "Unemployment Rate": {
        "id": "UNRATE",
        "description": "The percentage of the labor force that is unemployed."
    },
    "Consumer Price Index (CPI)": {
        "id": "CPIAUCSL",
        "description": "A measure of the average change over time in the prices paid by urban consumers for a market basket of consumer goods and services."
    },
    "10-Year Treasury Yield": {
        "id": "DGS10",
        "description": "The yield on the 10-Year Treasury Constant Maturity, widely used as a benchmark for mortgage rates and other interest rates."
    }
}

# --- Data Fetching Function ---
@st.cache_data(ttl=3600) # Cache data for 1 hour
def fetch_fred_data(series_id, api_key, start_date=None, end_date=None):
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
        "observation_end": end_date
    }
    try:
        response = requests.get(FRED_BASE_URL, params=params)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        observations = data.get("observations", [])
        df = pd.DataFrame(observations)

        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            # Convert '.' (missing values in FRED) to NaN
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True) # Ensure chronological order
            return df['value']
        else:
            return pd.Series(dtype='float64') # Return empty series if no data

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data for {series_id}: {e}")
        return pd.Series(dtype='float64')
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON for {series_id}: {e}")
        return pd.Series(dtype='float64')
    except Exception as e:
        st.error(f"An unexpected error occurred for {series_id}: {e}")
        return pd.Series(dtype='float64')


# --- Main Streamlit Application ---
def main():
    st.set_page_config(
        page_title="Public Data Visualizer",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 Public Data Visualizer Dashboard")

    st.markdown("""
    Explore key economic indicators with interactive charts.
    """)

    # --- ADD THIS NEW DISCLAIMER HERE ---
    st.info("""
    **Important Note:** This dashboard visualizes macroeconomic data fetched directly from the **FRED (Federal Reserve Economic Data) API**.
    Please be aware that economic data often has reporting lags (e.g., monthly, quarterly updates).
    The charts reflect the most current data available via the FRED API.
    Future updates may include additional indicators and data sources.
    """)
    # --- END OF DISCLAIMER ---


    st.sidebar.header("Select Indicator & Date Range")

    selected_indicator_name = st.sidebar.selectbox(
        "Choose an Economic Indicator",
        list(ECONOMIC_INDICATORS.keys())
    )

    selected_indicator_info = ECONOMIC_INDICATORS[selected_indicator_name]
    series_id = selected_indicator_info["id"]
    description = selected_indicator_info["description"]

    # Date Range selection
    today = pd.to_datetime("today").date()
    default_start_date = today - pd.DateOffset(years=10) # Default to last 10 years

    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=default_start_date)
    with col2:
        end_date = st.date_input("End Date", value=today)

    if start_date >= end_date:
        st.sidebar.error("Error: End Date must be after Start Date.")
        return

    st.subheader(f"{selected_indicator_name} Trends")
    st.markdown(f"*{description}*")


    with st.spinner(f"Fetching data for {selected_indicator_name}..."):
        data_series = fetch_fred_data(series_id, FRED_API_KEY, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

    if not data_series.empty:
        # Create a DataFrame for Plotly, ensuring 'date' is a column
        plot_df = data_series.reset_index()
        plot_df.columns = ['Date', 'Value'] # Rename columns for clarity

        fig = px.line(
            plot_df,
            x='Date',
            y='Value',
            title=f'{selected_indicator_name} Historical Data',
            labels={'Value': selected_indicator_name, 'Date': 'Date'},
            template='plotly_white'
        )

        fig.update_layout(hovermode="x unified") # Shows all traces on hover
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=5, label="5y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Raw Data (First 10 Rows)")
        st.dataframe(plot_df.head(10))

        st.markdown(
            f"Data Source: [FRED API - {selected_indicator_name}]({FRED_BASE_URL.replace('/series/observations', '')}/series/{series_id})"
        )

    else:
        st.warning(f"No data available for '{selected_indicator_name}' in the selected date range, or an error occurred.")


if __name__ == "__main__":
    main()