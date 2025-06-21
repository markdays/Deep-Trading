# Personal Quantitative Investment Agent

This project aims to provide tools and strategies for quantitative investment analysis.

## Project Structure

-   `quantitative_agent/src/`: Contains the source code for data fetching, feature engineering, strategy development, etc.
-   `quantitative_agent/data/`: Intended for storing downloaded data, processed features, etc. (currently not used by data_fetcher.py directly for saving).
-   `quantitative_agent/tests/`: Contains unit tests for the source code.

## Data Fetching

The primary way to get financial data into this system is through the functions provided in `quantitative_agent/src/data_fetcher.py`.

### Using `yfinance` for Global Market Data

The `fetch_stock_data` function leverages the `yfinance` library to download historical stock data from various global markets.

**Prerequisites:**
Ensure `yfinance` and `pandas` are installed:
```bash
pip install yfinance pandas
```

**Example:**
```python
from quantitative_agent.src.data_fetcher import fetch_stock_data

# Fetch data for Apple Inc. (AAPL)
aapl_data = fetch_stock_data(ticker="AAPL",
                             start_date="2023-01-01",
                             end_date="2023-12-31")
if not aapl_data.empty:
    print("Data for AAPL:")
    print(aapl_data.head())
```

### Using `pytdx` for A-Share OHLCV Data (China Market)

The `fetch_stock_data_pytdx` function allows you to fetch historical daily Open, High, Low, Close, and Volume (OHLCV) data for stocks listed on the Shanghai (SH) and Shenzhen (SZ) exchanges using the `pytdx` library.

**Prerequisites:**
Ensure `pytdx` and `pandas` are installed:
```bash
pip install pytdx pandas
```

**Example:**
```python
from quantitative_agent.src.data_fetcher import fetch_stock_data_pytdx

# Fetch data for a Shenzhen stock (e.g., Ping An Bank - 000001)
sz_stock_data = fetch_stock_data_pytdx(stock_code="000001",
                                       start_date="2023-10-01",
                                       end_date="2023-10-31")
if not sz_stock_data.empty:
    print("Data for SZ stock (000001):")
    print(sz_stock_data.head())

# Fetch data for a Shanghai stock (e.g., Kweichow Moutai - 600519)
sh_stock_data = fetch_stock_data_pytdx(stock_code="600519",
                                       start_date="2023-10-01",
                                       end_date="2023-10-31")
if not sh_stock_data.empty:
    print("\nData for SH stock (600519):")
    print(sh_stock_data.head())
```

This function infers the market (Shanghai or Shenzhen) from the stock code prefix and connects to TDX servers to retrieve the OHLCV data. It returns a pandas DataFrame with 'Open', 'High', 'Low', 'Close', 'Volume' columns and a DatetimeIndex.

### Fetching A-Share Financial Data (`pytdx.crawler`)

The `fetch_financial_data_pytdx` function retrieves historical financial statement data for a specified A-share stock and a specific financial reporting period. These periods are typically quarter-ends (e.g., "YYYY-03-31", "YYYY-06-30", "YYYY-09-30") or year-ends ("YYYY-12-31").

This function utilizes `pytdx.crawler`, which sources data from TDX's "gpcw" (公司财务 - Company Financials) data files. Each "gpcw" file contains financial indicators for all listed companies for that specific reporting date.

**Structure of Returned DataFrame:**
It's important to understand how the data is returned:
-   The DataFrame will contain one row of data if the requested stock is found for the period.
-   The **index** of the DataFrame is the **stock code** (e.g., "000001").
-   The **columns** are generically named by `pytdx` as `col1`, `col2`, ..., `colN`. A `report_date` column (parsed from the file content) is also included.
-   **To interpret what each `colX` represents (e.g., EPS, ROE, Total Assets), you MUST refer to an external mapping or official TDX documentation.** Common mappings can sometimes be found in other financial analysis projects that use TDX data (like the `financial_mean.py` dictionary from the QUANTAXIS project). This function provides the raw data structure as delivered by the `pytdx` crawler.

**Prerequisites:**
Make sure `pytdx` and `pandas` are installed:
```bash
pip install pytdx pandas
```

**Example:**
```python
from quantitative_agent.src.data_fetcher import fetch_financial_data_pytdx
import pandas as pd

# Ensure a specific report date is chosen for which data is likely available.
# Common report dates are "YYYY-03-31", "YYYY-06-30", "YYYY-09-30", "YYYY-12-31".
stock_code_example = "000001"  # Ping An Bank
# Use a report date known to have data, e.g., from test cases or
# by checking pytdx.crawler.HistoryFinancialListCrawler().fetch_and_parse()
report_date_example = "2023-06-30"

financial_dataframe = fetch_financial_data_pytdx(stock_code=stock_code_example,
                                                 report_date=report_date_example)

if not financial_dataframe.empty:
    print(f"Financial data for {stock_code_example} as of report date {report_date_example}:")
    # The DataFrame will have the stock_code as index and generic 'colX' columns.
    # The 'report_date' column (from the file) is also included.
    print(financial_dataframe.to_string()) # Using to_string() to print the full DataFrame if wide

    # To make sense of 'col1', 'col2', etc., you would refer to an external mapping.
    # For instance, if you know 'col1' is '基本每股收益' (Basic EPS) from an external mapping:
    # if 'col1' in financial_dataframe.columns:
    #     print(f"\nExample: Indicator 'col1' (e.g., Basic EPS): {financial_dataframe.iloc[0]['col1']}")
else:
    print(f"No financial data found for {stock_code_example} on {report_date_example}, "
          f"or the data file for this period might not be available on TDX servers.")
```

### Fetching Chinese Futures Market Data (AkShare)

The `fetch_futures_hist_akshare` function retrieves historical futures data (both daily and intraday) for Chinese futures markets using the `AkShare` library.

**Parameters:**
-   `symbol (str)`: The futures contract symbol.
    -   For daily main continuous contracts from Sina Finance (e.g., "RB0" for rebar steel, "IF0" for CSI 300 Index Future), use the Sina specific symbol. You can find a list of these using `akshare.futures_display_main_sina()`. `market_exchange` should typically be `None` for these.
    -   For specific daily contracts traded on exchanges (e.g., "rb2401" for rebar Jan 2024 contract, "if2401" for CSI 300 Index Future Jan 2024 contract), you must provide the `market_exchange`.
    -   For intraday data (also sourced from Sina), main continuous contract symbols (e.g., "RB0") or specific contract symbols (e.g., "rb2401") can often be used.
-   `start_date (str)`: Start date in "YYYY-MM-DD" format. Primarily used for daily data requests.
-   `end_date (str)`: End date in "YYYY-MM-DD" format. Primarily used for daily data requests.
-   `period (str, optional)`: Data period. Defaults to `'daily'`. Supported intraday options include `'1min'`, `'5min'`, `'15min'`, `'30min'`, `'60min'`. Intraday data is typically for the latest available trading day.
-   `market_exchange (str, optional)`: Required when fetching specific daily contracts from a particular exchange. Examples: `"CFFEX"` (China Financial Futures Exchange), `"SHFE"` (Shanghai Futures Exchange), `"DCE"` (Dalian Commodity Exchange), `"CZCE"` (Zhengzhou Commodity Exchange), `"INE"` (Shanghai International Energy Exchange), `"GFEX"` (Guangzhou Futures Exchange).

**Returned DataFrame:**
The function returns a pandas DataFrame with a DatetimeIndex. Columns typically include 'Open', 'High', 'Low', 'Close', 'Volume'. 'OpenInterest' and 'Settlement' columns are also included if available from the data source.

**Prerequisites:**
Ensure `akshare` and `pandas` are installed. It's recommended to keep AkShare updated for the latest fixes and symbol lists.
```bash
pip install akshare pandas --upgrade
```

**Examples:**

1.  **Fetch daily data for a Sina main continuous contract (e.g., Rebar Steel "RB0"):**
    ```python
    from quantitative_agent.src.data_fetcher import fetch_futures_hist_akshare

    # Fetches daily data for the main continuous rebar contract
    rb0_daily_data = fetch_futures_hist_akshare(
        symbol="RB0",
        start_date="2023-12-01",
        end_date="2023-12-31",
        period="daily"  # Can be omitted as it's the default
    )
    if not rb0_daily_data.empty:
        print("Daily data for RB0 (Sina Main Continuous):")
        print(rb0_daily_data.head())
    else:
        print("No daily data found for RB0 in the specified range or an error occurred.")
    ```

2.  **Fetch daily data for a specific exchange-traded contract (e.g., Gold "au2412" from SHFE):**
    ```python
    from quantitative_agent.src.data_fetcher import fetch_futures_hist_akshare

    # Note: Ensure "au2412" is/was an active contract for the chosen dates.
    # You might need to use a more current contract symbol for actual use.
    au2412_daily_data = fetch_futures_hist_akshare(
        symbol="au2412", # Specific contract code
        start_date="2023-12-01", # Adjust dates as needed for contract liquidity
        end_date="2023-12-31",
        period="daily",
        market_exchange="SHFE" # Shanghai Futures Exchange
    )
    if not au2412_daily_data.empty:
        print("\nDaily data for au2412 (SHFE specific contract):")
        print(au2412_daily_data.head())
    else:
        print("\nNo daily data found for au2412 (SHFE) in the specified range or an error occurred.")
    ```

3.  **Fetch 1-minute intraday data for a main continuous contract (e.g., CSI 300 Index Future "IF0"):**
    ```python
    from quantitative_agent.src.data_fetcher import fetch_futures_hist_akshare
    from datetime import datetime

    # Intraday data from AkShare (via Sina) is typically for the most recent trading day.
    # start_date and end_date parameters are not used by the underlying ak.futures_zh_minute_sina for date ranging.
    # Provide current date for clarity/logging, though it won't affect which day's data is fetched.
    today_str = datetime.today().strftime('%Y-%m-%d')

    if0_1min_data = fetch_futures_hist_akshare(
        symbol="IF0", # Main continuous CSI 300 Index Future
        start_date=today_str,
        end_date=today_str,
        period="1min"
    )
    if not if0_1min_data.empty:
        print("\n1-minute data for IF0 (Sina Intraday - latest available day):")
        print(if0_1min_data.tail()) # Show tail for most recent intraday data
    else:
        print("\nNo 1-minute intraday data found for IF0 (likely not a trading day or data source issue).")
    ```
