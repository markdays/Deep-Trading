import pandas as pd
import yfinance as yf
from pytdx.hq import TdxHq_API
from pytdx.config.hosts import hq_hosts
import random
from pytdx.crawler.history_financial_crawler import HistoryFinancialListCrawler, HistoryFinancialCrawler
import os
import tempfile

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
    (Docstring updated in previous step to reflect colX and index behavior)
    """
    try:
        date_obj = pd.to_datetime(report_date)
        filename = f"gpcw{date_obj.strftime('%Y%m%d')}.zip"

        list_crawler = HistoryFinancialListCrawler()
        available_files_data = list_crawler.fetch_and_parse()
        if available_files_data is None:
            print(f"Could not retrieve list of available financial data files.")
            return pd.DataFrame()

        available_files_df = pd.DataFrame(available_files_data)
        if filename not in available_files_df['filename'].values:
            print(f"Financial data file {filename} not found for report date {report_date}.")
            return pd.DataFrame()

        data_crawler = HistoryFinancialCrawler()

        with tempfile.TemporaryDirectory() as temp_dir:
            download_target_path = os.path.join(temp_dir, filename)
            raw_data_list = data_crawler.fetch_and_parse(filename=filename, path_to_download=download_target_path)

            if not raw_data_list:
                return pd.DataFrame()

            all_companies_df = data_crawler.to_df(raw_data_list)

            # Add check for all_companies_df being None
            if all_companies_df is None:
                print(f"Converting raw data to DataFrame for {filename} returned None.")
                return pd.DataFrame()

            if all_companies_df.empty:
                return pd.DataFrame()

            if stock_code not in all_companies_df.index:
                print(f"Stock code {stock_code} not found in index of financial data for {filename}.")
                return pd.DataFrame()

            stock_specific_data_df = all_companies_df.loc[[stock_code]].copy()

            for col in stock_specific_data_df.columns:
                if col != 'report_date':
                    stock_specific_data_df[col] = pd.to_numeric(stock_specific_data_df[col], errors='ignore')

            if 'report_date' in stock_specific_data_df.columns:
                 stock_specific_data_df['report_date'] = pd.to_datetime(stock_specific_data_df['report_date'].astype(str))

            return stock_specific_data_df

    except Exception as e:
        print(f"Error fetching financial data for {stock_code} on {report_date}: {e}")
        return pd.DataFrame()


if __name__ == '__main__':
    # Silenced yfinance and pytdx OHLCV tests for brevity

    print("\n--- Testing fetch_financial_data_pytdx ---")

    report_date_to_test = "2023-12-31"
    sz_stock_code_fin = "000001"
    sh_stock_code_fin = "600036" # Changed from 600036 for SH test

    print(f"\nFetching financial data for SZ stock {sz_stock_code_fin} on {report_date_to_test}")
    financial_data = fetch_financial_data_pytdx(stock_code=sz_stock_code_fin, report_date=report_date_to_test)
    if not financial_data.empty:
        print(f"Financial data for {sz_stock_code_fin} on {report_date_to_test} (first 5 rows, all columns):")
        print(financial_data.head().to_string())
    else:
        print(f"No financial data found for {sz_stock_code_fin} on {report_date_to_test}, or an error occurred.")

    invalid_report_date = "2023-10-10"
    print(f"\nFetching financial data for {sz_stock_code_fin} on invalid report date {invalid_report_date}")
    financial_data_invalid_date = fetch_financial_data_pytdx(stock_code=sz_stock_code_fin, report_date=invalid_report_date)
    if financial_data_invalid_date.empty:
        print(f"Correctly returned empty DataFrame for invalid report date {invalid_report_date}.")

    # Test the problematic 2023-09-30 date again
    previous_issue_date = "2023-09-30"
    print(f"\nFetching financial data for SH stock {sh_stock_code_fin} on {previous_issue_date}")
    financial_data_sh_prev = fetch_financial_data_pytdx(stock_code=sh_stock_code_fin, report_date=previous_issue_date)
    if not financial_data_sh_prev.empty:
        print(f"Financial data for {sh_stock_code_fin} on {previous_issue_date} (first 5 rows, all columns):")
        print(financial_data_sh_prev.head().to_string())
    else:
        print(f"No financial data found for {sh_stock_code_fin} on {previous_issue_date}, or an error occurred (expected if file is problematic).")
