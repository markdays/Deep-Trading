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
