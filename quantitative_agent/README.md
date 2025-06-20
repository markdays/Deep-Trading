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

### Using `pytdx` for A-shares (China Market)

The `fetch_stock_data_pytdx` function allows you to fetch historical daily data for stocks listed on the Shanghai (SH) and Shenzhen (SZ) exchanges using the `pytdx` library.

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
# Note: Stock 600036 (China Merchants Bank) was used in internal tests,
# 600519 (Kweichow Moutai) is another well-known example.
sh_stock_data = fetch_stock_data_pytdx(stock_code="600519",
                                       start_date="2023-10-01",
                                       end_date="2023-10-31")
if not sh_stock_data.empty:
    print("\nData for SH stock (600519):")
    print(sh_stock_data.head())
```

This function infers the market (Shanghai or Shenzhen) from the stock code prefix and connects to TDX servers to retrieve the data. It returns a pandas DataFrame with 'Open', 'High', 'Low', 'Close', 'Volume' columns and a DatetimeIndex.
