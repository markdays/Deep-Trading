import pandas as pd
import yfinance as yf
from pytdx.hq import TdxHq_API
# from pytdx.params import TDXParams # Not used for now, can be added if specific constants are needed
from pytdx.config.hosts import hq_hosts
import random # For selecting a random host

def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetches historical stock data (Open, High, Low, Close, Volume) for a given ticker
    and date range using the yfinance library.

    Args:
        ticker (str): The stock symbol (e.g., "AAPL" for Apple Inc.).
        start_date (str): The start date for the data in "YYYY-MM-DD" format.
        end_date (str): The end date for the data in "YYYY-MM-DD" format.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the OHLCV data with a DatetimeIndex,
                      sorted by date. Returns an empty DataFrame if an error occurs or
                      no data is found.
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            print(f"No data found for yfinance ticker {ticker} in the specified date range.")
            return pd.DataFrame()
        # Ensure columns are present before selecting
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            print(f"Missing columns {missing_cols} for yfinance ticker {ticker}. Available: {data.columns.tolist()}")
            return pd.DataFrame()
        # yfinance data already comes with DatetimeIndex and is typically sorted.
        return data[required_cols]
    except Exception as e:
        print(f"Error fetching data for yfinance ticker {ticker}: {e}")
        return pd.DataFrame()

def fetch_stock_data_pytdx(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetches historical daily stock data (Open, High, Low, Close, Volume) for
    Chinese A-share stocks using the pytdx library by connecting to TDX servers.

    The market (Shanghai or Shenzhen) is inferred from the stock code prefix.
    Stock codes starting with '6' are assumed to be Shanghai (market_id=1),
    while those starting with '0' or '3' are assumed to be Shenzhen (market_id=0).

    Args:
        stock_code (str): The stock code for a Chinese A-share.
                          Examples: "000001" (Ping An Bank, Shenzhen),
                                    "600036" (China Merchants Bank, Shanghai).
        start_date (str): The start date for the desired data range, formatted as "YYYY-MM-DD".
        end_date (str): The end date for the desired data range, formatted as "YYYY-MM-DD".

    Returns:
        pd.DataFrame: A pandas DataFrame containing the Open, High, Low, Close, and Volume
                      data for the specified stock and date range. The DataFrame will have
                      a DatetimeIndex and will be sorted by date.
                      Returns an empty DataFrame if an error occurs during fetching or
                      processing, if the stock code is invalid, if connection to TDX
                      servers fails, or if no data is found for the given period.
    """
    try:
        if stock_code.startswith('6'):
            market_id = 1  # Shanghai Stock Exchange
        elif stock_code.startswith('0') or stock_code.startswith('3'):
            market_id = 0  # Shenzhen Stock Exchange
        else:
            print(f"Invalid stock code format for pytdx: {stock_code}. Must start with '6', '0', or '3'.")
            return pd.DataFrame()

        api = TdxHq_API(auto_retry=True, raise_exception=False, heartbeat=True)

        valid_hosts = [(host_info[1], host_info[2]) for host_info in hq_hosts if isinstance(host_info, tuple) and len(host_info) >= 3]

        if not valid_hosts:
            print("No valid pytdx hq_hosts found.")
            return pd.DataFrame()

        connected = False
        for _ in range(min(5, len(valid_hosts))):
            server_ip, server_port = random.choice(valid_hosts)
            # print(f"Attempting to connect to pytdx server: {server_ip}:{server_port}") # Keep this commented out for less verbose output
            if api.connect(server_ip, server_port):
                connected = True
                # print(f"Successfully connected to pytdx server: {server_ip}:{server_port}")
                break
            # else:
                # print(f"Failed to connect to pytdx server: {server_ip}:{server_port}")

        if not connected:
            print("Failed to connect to any pytdx server after multiple attempts.")
            return pd.DataFrame()

        bars_to_fetch = 800
        data_list = api.get_security_bars(9, market_id, stock_code, 0, bars_to_fetch)

        if data_list is None:
            # print(f"No data returned from pytdx get_security_bars for {stock_code}. The stock code might be invalid or no data available.")
            api.disconnect()
            return pd.DataFrame()

        df = api.to_df(data_list)

        if df.empty:
            # print(f"No data for {stock_code} after converting to DataFrame or data is empty.")
            api.disconnect()
            return pd.DataFrame()

        required_pytdx_cols = {'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'vol': 'Volume'}
        df = df.rename(columns=required_pytdx_cols)

        if 'datetime' not in df.columns:
            if 'date' in df.columns:
                df['datetime'] = pd.to_datetime(df['date'])
            elif all(col in df.columns for col in ['year', 'month', 'day']):
                df['datetime'] = pd.to_datetime(df[['year', 'month', 'day']])
            else:
                # print(f"Cannot find or create 'datetime' column for {stock_code}.")
                api.disconnect()
                return pd.DataFrame()
        else:
             df['datetime'] = pd.to_datetime(df['datetime'])

        df = df.set_index('datetime')
        df = df[(df.index >= start_date) & (df.index <= end_date)]

        if df.empty:
            # print(f"No data for {stock_code} within the specified date range: {start_date} to {end_date} after filtering.")
            api.disconnect()
            return pd.DataFrame()

        final_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_final_cols = [col for col in final_cols if col not in df.columns]
        if missing_final_cols:
            # print(f"Missing essential columns {missing_final_cols} after processing for {stock_code}.")
            api.disconnect()
            return pd.DataFrame()

        df = df[final_cols]
        df = df.sort_index()

        api.disconnect()
        return df

    except Exception as e:
        print(f"An error occurred while fetching or processing data for {stock_code} with pytdx: {e}")
        if 'api' in locals() and hasattr(api, 'client') and api.client:
            api.disconnect()
        return pd.DataFrame()


if __name__ == '__main__':
    # Example usage for yfinance:
    print("--- Testing yfinance fetch_stock_data ---")
    aapl_data = fetch_stock_data("AAPL", "2023-01-01", "2023-12-31")
    if not aapl_data.empty:
        print("AAPL Data (yfinance):")
        print(aapl_data.head())
    else:
        print("Failed to fetch AAPL data using yfinance or data was empty.")

    invalid_data = fetch_stock_data("INVALIDTICKER", "2023-01-01", "2023-12-31")
    if invalid_data.empty:
        print("\nHandled invalid ticker example correctly (yfinance).")

    # Example usage for pytdx:
    print("\n--- Testing pytdx fetch_stock_data_pytdx ---")
    sh_stock_code = "600036"
    print(f"\nFetching data for Shanghai stock: {sh_stock_code}")
    sh_data = fetch_stock_data_pytdx(sh_stock_code, "2023-10-01", "2023-10-31") # Using a more recent range for example
    if not sh_data.empty:
        print(f"\nData for {sh_stock_code} (pytdx):")
        print(sh_data.head())
    else:
        print(f"Failed to fetch data for {sh_stock_code} using pytdx or data was empty for the period.")

    sz_stock_code = "000001"
    print(f"\nFetching data for Shenzhen stock: {sz_stock_code}")
    sz_data = fetch_stock_data_pytdx(sz_stock_code, "2023-10-01", "2023-10-31") # Using a more recent range for example
    if not sz_data.empty:
        print(f"\nData for {sz_stock_code} (pytdx):")
        print(sz_data.head())
    else:
        print(f"Failed to fetch data for {sz_stock_code} using pytdx or data was empty for the period.")

    invalid_pytdx_stock = "123456"
    print(f"\nFetching data for invalid pytdx stock: {invalid_pytdx_stock}")
    invalid_pytdx_data = fetch_stock_data_pytdx(invalid_pytdx_stock, "2023-01-01", "2023-01-31")
    if invalid_pytdx_data.empty:
        print(f"Handled invalid pytdx stock code {invalid_pytdx_stock} correctly.")

    non_existent_sh_stock = "609999"
    print(f"\nFetching data for non-existent Shanghai stock: {non_existent_sh_stock}")
    non_existent_sh_data = fetch_stock_data_pytdx(non_existent_sh_stock, "2023-01-01", "2023-01-31")
    if non_existent_sh_data.empty:
        print(f"Handled non-existent pytdx stock code {non_existent_sh_stock} correctly.")

    print(f"\nFetching future data for Shenzhen stock: {sz_stock_code}")
    future_data = fetch_stock_data_pytdx(sz_stock_code, "2030-01-01", "2030-01-31")
    if future_data.empty:
        print(f"Handled future date range for {sz_stock_code} correctly (empty data expected).")
    else:
        print(f"Future data for {sz_stock_code} (pytdx):")
        print(future_data)
