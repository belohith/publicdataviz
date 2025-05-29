# 📊 Public Data Visualizer Dashboard

This Streamlit dashboard provides an interactive platform to explore key economic indicators sourced from the FRED (Federal Reserve Economic Data) API. Users can select various data series and filter by date range to visualize historical trends and gain insights into macroeconomic movements.

## ✨ Features

* **Multi-Series Data Visualization:** Choose from a curated list of economic indicators (e.g., Federal Funds Rate, Real GDP, Unemployment Rate, CPI, 10-Year Treasury Yield).
* **Interactive Time Series Plots:** Utilizes **Plotly Express** to generate dynamic and zoomable line charts with built-in date range selectors.
* **Date Range Filtering:** Customize the displayed data period using intuitive date pickers.
* **Real-time Data Fetching:** Integrates with the FRED API to fetch up-to-date economic data.
* **Data Preprocessing:** Handles data type conversions and missing value imputation (e.g., converting '.' to NaN).
* **Secure API Key Handling:** Utilizes Streamlit's `secrets.toml` for secure management of API keys.
* **Informative UI:** Provides descriptions and source links for each economic indicator.

## 🛠️ Technologies Used

* **Python**
* **Streamlit:** For building the interactive web dashboard.
* **Pandas:** For efficient data manipulation, cleaning, and analysis.
* **Requests:** For making HTTP requests to the FRED API.
* **Plotly Express:** For creating rich, interactive data visualizations.
* **Matplotlib / Seaborn (installed but primary focus is Plotly):** General plotting utilities.

## 🔑 API Key Setup

1.  **Obtain a FRED API Key:**
    * Go to `https://fred.stlouisfed.org/docs/api/api_key.html` and follow the instructions to request a free API key.

2.  **Store the key securely:**
    * In your project directory (`public_data_visualizer`), create a folder named `.streamlit` if it doesn't exist.
    * Inside `.streamlit`, create a file named `secrets.toml`.
    * Add your FRED API key to `secrets.toml` like this:
        ```toml
        FRED_API_KEY = "YOUR_ACTUAL_FRED_API_KEY_HERE"
        ```
        (Replace `YOUR_ACTUAL_FRED_API_KEY_HERE` with your actual key.)

## 🚀 How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YourGitHubUsername/public-data-visualizer.git](https://github.com/YourGitHubUsername/public-data-visualizer.git)
    cd public-data-visualizer
    ```
    (Replace `YourGitHubUsername` with your actual GitHub username and adjust repo name if different.)

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install streamlit pandas requests plotly matplotlib seaborn
    ```

4.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

5.  The application will open in your web browser, usually at `http://localhost:8501`.

## 💡 Usage

1.  Select an economic indicator from the dropdown menu in the sidebar.
2.  Adjust the "Start Date" and "End Date" to filter the data.
3.  Interact with the Plotly chart (zoom, pan, use range selectors).

## ✍️ Author

Lohith Bollineni

## 📄 License

This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).