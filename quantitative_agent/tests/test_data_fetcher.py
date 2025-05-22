import pytest
import pandas as pd
from quantitative_agent.src.data_fetcher import fetch_stock_data

# Test with a valid ticker and date range
def test_fetch_valid_data():
    """
    Tests fetch_stock_data with a valid ticker and date range.
    """
    ticker = "AAPL"
    start_date = "2023-01-01"
    end_date = "2023-01-31"
    data = fetch_stock_data(ticker, start_date, end_date)

    assert isinstance(data, pd.DataFrame), "Function should return a pandas DataFrame."
    assert not data.empty, "DataFrame should not be empty for valid data."
    
    expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in expected_columns:
        assert col in data.columns, f"DataFrame should contain column: {col}"

# Test with an invalid ticker
def test_fetch_invalid_ticker():
    """
    Tests fetch_stock_data with an invalid ticker.
    """
    ticker = "INVALIDTICKERXYZ"
    start_date = "2023-01-01"
    end_date = "2023-01-31"
    data = fetch_stock_data(ticker, start_date, end_date)

    assert isinstance(data, pd.DataFrame), "Function should return a pandas DataFrame for invalid ticker."
    assert data.empty, "DataFrame should be empty for an invalid ticker."

# Test with a date range yielding no data
def test_fetch_no_data_range():
    """
    Tests fetch_stock_data with a date range that should yield no data.
    (e.g., a weekend or a period the stock was not trading)
    """
    ticker = "AAPL"
    # Using dates that are likely to be a weekend or holiday period with no trading
    start_date = "2024-01-06" # Saturday
    end_date = "2024-01-07"   # Sunday
    data = fetch_stock_data(ticker, start_date, end_date)

    assert isinstance(data, pd.DataFrame), "Function should return a pandas DataFrame."
    assert data.empty, "DataFrame should be empty for a date range with no trading data."

# Test with a ticker that exists but had no data for the specific short period
def test_fetch_ticker_no_data_for_period():
    """
    Tests fetch_stock_data for a valid ticker but a very specific, short,
    and unlikely trading period (e.g., future dates not yet traded).
    """
    ticker = "GOOG" # A valid ticker
    start_date = "2030-01-01" # A future date
    end_date = "2030-01-02"   # A future date
    data = fetch_stock_data(ticker, start_date, end_date)

    assert isinstance(data, pd.DataFrame), "Function should return a pandas DataFrame."
    assert data.empty, "DataFrame should be empty if no data exists for the period."
