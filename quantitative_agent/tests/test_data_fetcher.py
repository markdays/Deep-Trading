import pytest
import pandas as pd
from quantitative_agent.src.data_fetcher import fetch_stock_data, fetch_stock_data_pytdx

# Constants for pytdx tests
VALID_SH_STOCK = "600036"  # China Merchants Bank (Shanghai)
VALID_SZ_STOCK = "000001"  # Ping An Bank (Shenzhen)
START_DATE_VALID = "2023-10-09" # Monday
END_DATE_VALID = "2023-10-13"   # Friday (covers a week)
SINGLE_DAY_DATE = "2023-10-09"  # Monday, likely a trading day
START_DATE_FUTURE = "2099-01-01"
END_DATE_FUTURE = "2099-01-05"
EXPECTED_COLUMNS = ['Open', 'High', 'Low', 'Close', 'Volume']

# --- Tests for fetch_stock_data (yfinance) ---

def test_fetch_valid_data():
    """
    Tests fetch_stock_data with a valid ticker and date range.
    """
    ticker = "AAPL"
    start_date = "2023-01-01"
    end_date = "2023-01-31"
    data = fetch_stock_data(ticker, start_date, end_date)

    assert isinstance(data, pd.DataFrame), "Function should return a pandas DataFrame."
    assert not data.empty, "DataFrame should not be empty for valid data (AAPL yfinance)."

    for col in EXPECTED_COLUMNS:
        assert col in data.columns, f"DataFrame should contain column: {col}"

def test_fetch_invalid_ticker():
    """
    Tests fetch_stock_data with an invalid ticker.
    """
    ticker = "INVALIDTICKERXYZ"
    start_date = "2023-01-01"
    end_date = "2023-01-31"
    data = fetch_stock_data(ticker, start_date, end_date)

    assert isinstance(data, pd.DataFrame), "Function should return a pandas DataFrame for invalid ticker (yfinance)."
    assert data.empty, "DataFrame should be empty for an invalid ticker (yfinance)."

def test_fetch_no_data_range():
    """
    Tests fetch_stock_data with a date range that should yield no data.
    """
    ticker = "AAPL"
    start_date = "2024-01-06" # Saturday
    end_date = "2024-01-07"   # Sunday
    data = fetch_stock_data(ticker, start_date, end_date)

    assert isinstance(data, pd.DataFrame), "Function should return a pandas DataFrame (yfinance)."
    assert data.empty, "DataFrame should be empty for a date range with no trading data (yfinance)."

def test_fetch_ticker_no_data_for_period():
    """
    Tests fetch_stock_data for a valid ticker but a future date range.
    """
    ticker = "GOOG"
    start_date = "2030-01-01"
    end_date = "2030-01-02"
    data = fetch_stock_data(ticker, start_date, end_date)

    assert isinstance(data, pd.DataFrame), "Function should return a pandas DataFrame (yfinance)."
    assert data.empty, "DataFrame should be empty if no data exists for the period (yfinance)."

# --- Tests for fetch_stock_data_pytdx ---

@pytest.mark.pytdx # Optional: mark tests that make external calls
def test_fetch_sh_stock_valid_range_pytdx():
    """Tests fetching data for a Shanghai stock over a valid date range."""
    data = fetch_stock_data_pytdx(VALID_SH_STOCK, START_DATE_VALID, END_DATE_VALID)
    assert isinstance(data, pd.DataFrame), f"SH stock ({VALID_SH_STOCK}) fetch should return DataFrame."
    assert not data.empty, f"SH stock ({VALID_SH_STOCK}) data should not be empty for range {START_DATE_VALID}-{END_DATE_VALID}."
    assert isinstance(data.index, pd.DatetimeIndex), f"SH stock ({VALID_SH_STOCK}) index should be DatetimeIndex."
    for col in EXPECTED_COLUMNS:
        assert col in data.columns, f"SH stock ({VALID_SH_STOCK}) DataFrame missing column: {col}."
    assert data.index.min() >= pd.to_datetime(START_DATE_VALID), f"SH stock ({VALID_SH_STOCK}) data starts before {START_DATE_VALID}."
    assert data.index.max() <= pd.to_datetime(END_DATE_VALID), f"SH stock ({VALID_SH_STOCK}) data ends after {END_DATE_VALID}."
    # Check if all dates are within the range (inclusive of start and end)
    assert all((data.index >= pd.to_datetime(START_DATE_VALID)) & (data.index <= pd.to_datetime(END_DATE_VALID))), \
        f"Not all dates for SH stock ({VALID_SH_STOCK}) are within {START_DATE_VALID} and {END_DATE_VALID}"


@pytest.mark.pytdx
def test_fetch_sz_stock_valid_range_pytdx():
    """Tests fetching data for a Shenzhen stock over a valid date range."""
    data = fetch_stock_data_pytdx(VALID_SZ_STOCK, START_DATE_VALID, END_DATE_VALID)
    assert isinstance(data, pd.DataFrame), f"SZ stock ({VALID_SZ_STOCK}) fetch should return DataFrame."
    assert not data.empty, f"SZ stock ({VALID_SZ_STOCK}) data should not be empty for range {START_DATE_VALID}-{END_DATE_VALID}."
    assert isinstance(data.index, pd.DatetimeIndex), f"SZ stock ({VALID_SZ_STOCK}) index should be DatetimeIndex."
    for col in EXPECTED_COLUMNS:
        assert col in data.columns, f"SZ stock ({VALID_SZ_STOCK}) DataFrame missing column: {col}."
    assert data.index.min() >= pd.to_datetime(START_DATE_VALID), f"SZ stock ({VALID_SZ_STOCK}) data starts before {START_DATE_VALID}."
    assert data.index.max() <= pd.to_datetime(END_DATE_VALID), f"SZ stock ({VALID_SZ_STOCK}) data ends after {END_DATE_VALID}."
    assert all((data.index >= pd.to_datetime(START_DATE_VALID)) & (data.index <= pd.to_datetime(END_DATE_VALID))), \
        f"Not all dates for SZ stock ({VALID_SZ_STOCK}) are within {START_DATE_VALID} and {END_DATE_VALID}"


@pytest.mark.pytdx
def test_fetch_invalid_stock_code_pytdx():
    """Tests fetching data with an invalid stock code format."""
    data = fetch_stock_data_pytdx("INVALIDCODE", START_DATE_VALID, END_DATE_VALID)
    assert isinstance(data, pd.DataFrame), "Invalid stock code fetch should return DataFrame."
    assert data.empty, "DataFrame should be empty for an invalid stock code format."

@pytest.mark.pytdx
def test_fetch_non_existent_stock_code_pytdx():
    """Tests fetching data for a stock code that is valid format but likely non-existent."""
    data = fetch_stock_data_pytdx("609999", START_DATE_VALID, END_DATE_VALID) # Valid SH format
    assert isinstance(data, pd.DataFrame), "Non-existent stock code fetch should return DataFrame."
    assert data.empty, "DataFrame should be empty for a non-existent stock code."

@pytest.mark.pytdx
def test_fetch_future_date_range_pytdx():
    """Tests fetching data for a future date range."""
    data = fetch_stock_data_pytdx(VALID_SH_STOCK, START_DATE_FUTURE, END_DATE_FUTURE)
    assert isinstance(data, pd.DataFrame), "Future date range fetch should return DataFrame."
    assert data.empty, "DataFrame should be empty for a future date range."

@pytest.mark.pytdx
def test_fetch_single_day_range_pytdx():
    """Tests fetching data for a single valid trading day."""
    data = fetch_stock_data_pytdx(VALID_SH_STOCK, SINGLE_DAY_DATE, SINGLE_DAY_DATE)
    assert isinstance(data, pd.DataFrame), f"Single day fetch for {VALID_SH_STOCK} should return DataFrame."
    if not data.empty: # It's possible the single day was a holiday or no trading
        assert len(data) == 1, f"DataFrame should have 1 row for a single trading day ({SINGLE_DAY_DATE}), got {len(data)}."
        assert data.index[0] == pd.to_datetime(SINGLE_DAY_DATE), f"Data index should be {SINGLE_DAY_DATE}."
        for col in EXPECTED_COLUMNS:
            assert col in data.columns, f"Single day DataFrame for {VALID_SH_STOCK} missing column: {col}."
    else:
        # This is acceptable if SINGLE_DAY_DATE was unexpectedly not a trading day for this stock
        print(f"Warning: Data for single day {SINGLE_DAY_DATE} for {VALID_SH_STOCK} was empty. This might be okay if it was a non-trading day.")
        pass # Pass the test if empty, as the function should handle this gracefully.

@pytest.mark.pytdx
def test_fetch_date_range_with_no_trading_pytdx():
    """Tests fetching data for a date range known to have no trading (e.g., long holiday)."""
    # Example: Chinese New Year 2024 was roughly Feb 10-17. Let's pick a range within that.
    start_no_trade = "2024-02-12"
    end_no_trade = "2024-02-16"
    data = fetch_stock_data_pytdx(VALID_SH_STOCK, start_no_trade, end_no_trade)
    assert isinstance(data, pd.DataFrame), "Fetch over non-trading period should return DataFrame."
    assert data.empty, f"DataFrame should be empty for a known non-trading period ({start_no_trade} - {end_no_trade})."

# To run tests with pytest, navigate to the parent directory of 'quantitative_agent'
# and run: python -m pytest -s quantitative_agent/tests/test_data_fetcher.py
# The -s flag shows print statements, useful for debugging.
# The @pytest.mark.pytdx is optional but can be used to group tests or skip them.
# e.g., pytest -m "not pytdx" to skip these, or pytest -m pytdx to run only these.
# (Requires registering the mark in pytest.ini or conftest.py if you want to avoid warnings)

# Example pytest.ini content to register the mark:
# [pytest]
# markers =
#     pytdx: marks tests as using the pytdx library (makes live network calls)

# For now, we'll just run them directly.
# It's assumed that the pytdx library is installed and network access is available.
# The tests for yfinance are kept as they were.
# The `fetch_stock_data_pytdx` might print connection attempts; this is normal.
# If pytdx servers are unavailable, these tests might fail due to empty DataFrames when data is expected.
# This is an inherent aspect of testing live external APIs.
# For CI/CD, such tests are often mocked or run against dedicated test servers.
# For this exercise, live calls are acceptable per instructions.File 'quantitative_agent/tests/test_data_fetcher.py' overwritten successfully.
