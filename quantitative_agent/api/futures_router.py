from fastapi import APIRouter, HTTPException
import pandas as pd
from quantitative_agent.src import data_fetcher
from . import schemas # Assuming schemas.py is in the same directory

router = APIRouter()

@router.post("/history/akshare/", summary="Fetch Futures historical OHLCV data via AkShare")
async def get_akshare_futures_hist(request: schemas.FuturesHistRequest):
    try:
        df = data_fetcher.fetch_futures_hist_akshare(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            period=request.period,
            market_exchange=request.market_exchange
        )
        if df.empty:
            return []

        # Ensure index is DatetimeIndex before strftime, then format
        if not isinstance(df.index, pd.DatetimeIndex):
             df.index = pd.to_datetime(df.index)

        # AkShare futures data index is 'Date' after processing in data_fetcher
        # Determine format based on period
        if request.period == 'daily':
            date_format = '%Y-%m-%d'
        else: # Intraday typically includes time
            date_format = '%Y-%m-%d %H:%M:%S'

        df.index = df.index.strftime(date_format)

        # Convert NA to None for JSON compatibility if pd.NA was used
        df_dict = df.reset_index().to_dict(orient='records')
        # Pandas to_dict with 'records' should handle pd.NA to None automatically if version is recent enough.
        # If not, manual conversion might be needed:
        # for record in df_dict:
        #     for key, value in record.items():
        #         if pd.isna(value):
        #             record[key] = None
        return df_dict
    except Exception as e:
        print(f"Error in get_akshare_futures_hist: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
