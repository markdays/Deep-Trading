import pandas as pd
import yfinance as yf
from pytdx.hq import TdxHq_API
from pytdx.config.hosts import hq_hosts
import random
from pytdx.crawler.history_financial_crawler import HistoryFinancialListCrawler, HistoryFinancialCrawler
import os
import tempfile
import akshare as ak # Added AkShare import

def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetches historical stock data (Open, High, Low, Close, Volume) for a given ticker
    and date range using the yfinance library.
    (Docstring remains the same)
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty: return pd.DataFrame()
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols: return pd.DataFrame()
        return data[required_cols]
    except Exception as e:
        return pd.DataFrame()

def fetch_stock_data_pytdx(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetches historical daily stock data (Open, High, Low, Close, Volume) for
    Chinese A-share stocks using the pytdx library by connecting to TDX servers.
    (Docstring remains the same)
    """
    try:
        if stock_code.startswith('6'): market_id = 1
        elif stock_code.startswith('0') or stock_code.startswith('3'): market_id = 0
        else: return pd.DataFrame()

        api = TdxHq_API(auto_retry=True, raise_exception=False, heartbeat=True)
        valid_hosts = [(h[1], h[2]) for h in hq_hosts if isinstance(h, tuple) and len(h) >= 3]
        if not valid_hosts: return pd.DataFrame()

        connected = False
        for _ in range(min(5, len(valid_hosts))):
            server_ip, server_port = random.choice(valid_hosts)
            if api.connect(server_ip, server_port):
                connected = True
                break
        if not connected: return pd.DataFrame()

        data_list = api.get_security_bars(9, market_id, stock_code, 0, 800)
        api.disconnect()

        if data_list is None: return pd.DataFrame()
        df = api.to_df(data_list)
        if df.empty: return pd.DataFrame()

        df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'vol': 'Volume'})

        if 'datetime' not in df.columns:
            if 'date' in df.columns: df['datetime'] = pd.to_datetime(df['date'])
            elif all(c in df.columns for c in ['year', 'month', 'day']): df['datetime'] = pd.to_datetime(df[['year', 'month', 'day']])
            else: return pd.DataFrame()
        else: df['datetime'] = pd.to_datetime(df['datetime'])

        df = df.set_index('datetime')
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        if df.empty: return pd.DataFrame()

        final_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if any(c not in df.columns for c in final_cols): return pd.DataFrame()

        return df[final_cols].sort_index()
    except Exception as e:
        if 'api' in locals() and hasattr(api, 'client') and api.client: api.disconnect()
        return pd.DataFrame()

def fetch_financial_data_pytdx(stock_code: str, report_date: str) -> pd.DataFrame:
    """
    Fetches historical financial data for a specific A-share stock and reporting period
    using pytdx.crawler.
    (Docstring remains the same as previous correct version)
    """
    try:
        date_obj = pd.to_datetime(report_date)
        filename = f"gpcw{date_obj.strftime('%Y%m%d')}.zip"

        list_crawler = HistoryFinancialListCrawler()
        available_files_data = list_crawler.fetch_and_parse()
        if available_files_data is None:
            return pd.DataFrame()

        available_files_df = pd.DataFrame(available_files_data)
        if filename not in available_files_df['filename'].values:
            return pd.DataFrame()

        data_crawler = HistoryFinancialCrawler()

        with tempfile.TemporaryDirectory() as temp_dir:
            download_target_path = os.path.join(temp_dir, filename)
            raw_data_list = data_crawler.fetch_and_parse(filename=filename, path_to_download=download_target_path)

            if not raw_data_list: return pd.DataFrame()
            all_companies_df = data_crawler.to_df(raw_data_list)
            if all_companies_df is None: return pd.DataFrame()
            if all_companies_df.empty: return pd.DataFrame()

            if stock_code not in all_companies_df.index:
                return pd.DataFrame()

            stock_specific_data_df = all_companies_df.loc[[stock_code]].copy() # Explicit copy

            for col in stock_specific_data_df.columns:
                if col != 'report_date':
                    stock_specific_data_df[col] = pd.to_numeric(stock_specific_data_df[col], errors='ignore')

            if 'report_date' in stock_specific_data_df.columns:
                 stock_specific_data_df['report_date'] = pd.to_datetime(stock_specific_data_df['report_date'].astype(str))
            return stock_specific_data_df
    except Exception as e:
        return pd.DataFrame()

def fetch_futures_hist_akshare(
    symbol: str,
    start_date: str,
    end_date: str,
    period: str = 'daily',
    market_exchange: str = None
) -> pd.DataFrame:
    """
    Fetches historical futures data using AkShare.
    (Docstring remains same as in prompt)
    """
    print(f"Attempting to fetch AkShare futures data for: symbol={symbol}, period={period}, "
          f"start={start_date}, end={end_date}, market={market_exchange}")
    try:
        df = pd.DataFrame() # Initialize df as an empty DataFrame
        if period == 'daily':
            is_sina_main_contract = symbol.isupper() and (symbol.endswith('0') or symbol.endswith('88') or symbol.endswith('888'))

            if is_sina_main_contract and not market_exchange:
                print(f"Fetching daily main continuous contract (Sina) for {symbol}...")
                ak_start_date = start_date.replace('-', '')
                ak_end_date = end_date.replace('-', '')
                # Assign directly to df, no need to initialize as empty then reassign if it's the main path
                df = ak.futures_main_sina(symbol=symbol, start_date=ak_start_date, end_date=ak_end_date)
                if df.empty: return pd.DataFrame() # Return early if AkShare gives empty

                rename_map_sina = {
                    '日期': 'date', '开盘价': 'open', '最高价': 'high',
                    '最低价': 'low', '收盘价': 'close', '成交量': 'volume',
                    '持仓量': 'open_interest', '动态结算价': 'settlement'
                }
                if '动态结算价' not in df.columns and '结算价' in df.columns:
                    rename_map_sina['结算价'] = 'settlement'
                df.rename(columns=rename_map_sina, inplace=True)

            elif market_exchange:
                print(f"Fetching specific daily contract from exchange {market_exchange} for {symbol}...")
                all_data_df = ak.get_futures_daily(
                    start_date=start_date.replace('-', ''),
                    end_date=end_date.replace('-', ''),
                    market=market_exchange.upper()
                )
                if all_data_df.empty: return pd.DataFrame()

                # Addressing SettingWithCopyWarning by using .copy()
                df_filtered_lower = all_data_df[all_data_df['symbol'].str.lower() == symbol.lower()]
                if not df_filtered_lower.empty:
                    df = df_filtered_lower.copy()
                elif not symbol.islower():
                    df_filtered_upper = all_data_df[all_data_df['symbol'].str.upper() == symbol.upper()]
                    if not df_filtered_upper.empty:
                        df = df_filtered_upper.copy()
                    # else df remains empty, initialized at start of try block
                # else df remains empty

                if df.empty: # If after checks, df is still the one initialized at the start (empty)
                    print(f"Symbol {symbol} not found in data from exchange {market_exchange}.")
                    return pd.DataFrame()

                if 'settle' in df.columns and 'settlement' not in df.columns:
                    df.rename(columns={'settle': 'settlement'}, inplace=True)

            else:
                print("For specific daily contracts (non-Sina main), `market_exchange` must be provided.")
                return pd.DataFrame()

        elif period in ['1min', '5min', '15min', '30min', '60min']:
            print(f"Fetching {period} intraday data (Sina) for {symbol}...")
            df = ak.futures_zh_minute_sina(symbol=symbol.upper(), period=period.replace('min',''))
            if df.empty: return pd.DataFrame()
            df.rename(columns={'hold': 'open_interest', 'datetime': 'date'}, inplace=True)
        else:
            print(f"Unsupported period: {period}")
            return pd.DataFrame()

        if df.empty: # Catch-all if df is empty at this point
            print(f"No data returned from AkShare for {symbol} with period {period}.")
            return pd.DataFrame()

        final_rename_map = {
            'date': 'Date',
            'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close',
            'volume': 'Volume', 'open_interest': 'OpenInterest', 'settlement': 'Settlement'
        }
        df.rename(columns=final_rename_map, inplace=True)

        if 'Date' not in df.columns:
             print("Date column not found after processing.")
             return pd.DataFrame()

        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        final_cols_order = ['Open', 'High', 'Low', 'Close', 'Volume']
        if 'OpenInterest' in df.columns: final_cols_order.append('OpenInterest')
        if 'Settlement' in df.columns: final_cols_order.append('Settlement')

        for col in final_cols_order:
            if col not in df.columns:
                df[col] = pd.NA

        return df[final_cols_order].sort_index()

    except Exception as e:
        print(f"Error fetching futures data for {symbol} with AkShare: {e}")
        return pd.DataFrame()


if __name__ == '__main__':
    # Silenced other tests

    print("\n--- Testing fetch_futures_hist_akshare ---")

    rb0_daily = fetch_futures_hist_akshare(symbol="RB0", start_date="2024-01-01", end_date="2024-01-31", period="daily")
    if not rb0_daily.empty: print("\nRB0 Daily (Sina Main Continuous): Fetched.")
    else: print("\nRB0 Daily (Sina Main Continuous): No data or error.")

    ag_daily_specific = fetch_futures_hist_akshare(symbol="ag2409", start_date="2024-03-01", end_date="2024-03-31", period="daily", market_exchange="SHFE")
    if not ag_daily_specific.empty: print("\nag2409 Daily (SHFE Specific Contract): Fetched.")
    else: print("\nag2409 Daily (SHFE Specific Contract): No data or error.")

    rb0_1min = fetch_futures_hist_akshare(symbol="RB0", start_date="2024-04-01", end_date="2024-04-01", period="1min")
    if not rb0_1min.empty: print("\nRB0 1-min (Sina Intraday): Fetched.")
    else: print("\nRB0 1-min (Sina Intraday): No data or error.")

    invalid_futures = fetch_futures_hist_akshare(symbol="INVALIDFUT", start_date="2024-01-01", end_date="2024-01-31")
    if invalid_futures.empty: print("\nCorrectly returned empty for INVALIDFUT.")
    else: print("\nData returned for INVALIDFUT - check logic.")

    if0_daily = fetch_futures_hist_akshare(symbol="IF0", start_date="2024-01-01", end_date="2024-01-31", period="daily")
    if not if0_daily.empty: print("\nIF0 Daily (Sina Main Continuous): Fetched.")
    else: print("\nIF0 Daily (Sina Main Continuous): No data or error.")

    if_daily_specific = fetch_futures_hist_akshare(symbol="IF2404", start_date="2024-03-01", end_date="2024-03-31", period="daily", market_exchange="CFFEX")
    if not if_daily_specific.empty: print("\nIF2404 Daily (CFFEX Specific Contract): Fetched.")
    else: print("\nIF2404 Daily (CFFEX Specific Contract): No data or error.")
