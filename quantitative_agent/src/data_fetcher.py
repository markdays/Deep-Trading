import pandas as pd
import yfinance as yf

def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetches historical stock data (Open, High, Low, Close, Volume) for a given ticker
    and date range using the yfinance library.

    Args:
        ticker (str): The stock symbol (e.g., "AAPL").
        start_date (str): The start date for the data in "YYYY-MM-DD" format.
        end_date (str): The end date for the data in "YYYY-MM-DD" format.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the OHLCV data,
                      or an empty DataFrame if an error occurs.
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            print(f"No data found for ticker {ticker} in the specified date range.")
            return pd.DataFrame()
        return data[['Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception as e:
        print(f"Error fetching data for ticker {ticker}: {e}")
        return pd.DataFrame()

if __name__ == '__main__':
    # Example usage:
    aapl_data = fetch_stock_data("AAPL", "2023-01-01", "2023-12-31")
    if not aapl_data.empty:
        print("AAPL Data:")
        print(aapl_data.head())

    # Example of an invalid ticker
    invalid_data = fetch_stock_data("INVALIDTICKER", "2023-01-01", "2023-12-31")
    if invalid_data.empty:
        print("\nHandled invalid ticker example correctly.")

    # Example of a date range with no data (e.g., a very recent future date or a weekend for all days)
    no_data_range = fetch_stock_data("GOOG", "2024-01-06", "2024-01-07") # Assuming these are weekend days
    if no_data_range.empty:
        print("\nHandled date range with no data correctly.")
    
    # Example with a valid ticker that might have had issues in the past (though yfinance is robust)
    # tsla_data = fetch_stock_data("TSLA", "2020-01-01", "2020-01-31")
    # if not tsla_data.empty:
    # print("\nTSLA Data:")
    # print(tsla_data.head())
