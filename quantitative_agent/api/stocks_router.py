from fastapi import APIRouter, HTTPException, Query
import pandas as pd
from quantitative_agent.src import data_fetcher
from . import schemas # Assuming schemas.py is in the same directory

router = APIRouter()

@router.post("/ohlcv/yfinance/", summary="Fetch OHLCV data via yfinance")
async def get_yfinance_ohlcv(request: schemas.StockOhlcvRequest):
    try:
        df = data_fetcher.fetch_stock_data(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date
        )
        if df.empty:
            return []
        if not isinstance(df.index, pd.DatetimeIndex):
             df.index = pd.to_datetime(df.index)
        # Standardize Date column name after reset_index
        df_reset = df.reset_index()
        df_reset.rename(columns={df_reset.columns[0]: 'Date'}, inplace=True)
        df_reset['Date'] = pd.to_datetime(df_reset['Date']).dt.strftime('%Y-%m-%d')
        return df_reset.to_dict(orient='records')
    except Exception as e:
        print(f"Error in get_yfinance_ohlcv: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/ohlcv/pytdx/", summary="Fetch A-Share OHLCV data via pytdx")
async def get_pytdx_ohlcv(request: schemas.PytdxStockOhlcvRequest):
    try:
        df = data_fetcher.fetch_stock_data_pytdx(
            stock_code=request.stock_code,
            start_date=request.start_date,
            end_date=request.end_date
        )
        if df.empty:
            return []
        if not isinstance(df.index, pd.DatetimeIndex):
             df.index = pd.to_datetime(df.index)
        df_reset = df.reset_index()
        df_reset.rename(columns={df_reset.columns[0]: 'Date'}, inplace=True)
        # pytdx OHLCV data usually includes time from get_security_bars
        df_reset['Date'] = pd.to_datetime(df_reset['Date']).dt.strftime('%Y-%m-%d %H:%M:%S')
        return df_reset.to_dict(orient='records')
    except Exception as e:
        print(f"Error in get_pytdx_ohlcv: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/financials/pytdx/", summary="Fetch A-Share financial statement data via pytdx.crawler")
async def get_pytdx_financial_data(request: schemas.FinancialDataRequest):
    try:
        df = data_fetcher.fetch_financial_data_pytdx(
            stock_code=request.stock_code,
            report_date=request.report_date
        )
        if df.empty:
            return []
        # Financial data has stock_code as index. 'report_date' is a column.
        # No specific date formatting needed here as it's already handled in fetch function or is data.
        # `to_dict` will handle Timestamp if 'report_date' column is Timestamp.
        # If 'report_date' column is already string, it's fine.
        # Ensure 'report_date' (the column from pytdx, not the request param) is string for JSON.
        if 'report_date' in df.columns and isinstance(df['report_date'].iloc[0], pd.Timestamp):
             df['report_date'] = df['report_date'].dt.strftime('%Y-%m-%d')

        return df.reset_index().to_dict(orient='records') # reset_index converts stock_code index to column
    except Exception as e:
        print(f"Error in get_pytdx_financial_data: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
