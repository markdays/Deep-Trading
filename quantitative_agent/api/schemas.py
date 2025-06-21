from typing import Optional
from pydantic import BaseModel, Field

class StockOhlcvRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., 'AAPL', '000001.SZ', '600036.SS')")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")

class PytdxStockOhlcvRequest(BaseModel):
    stock_code: str = Field(..., description="Stock code (e.g., '000001', '600036') for pytdx")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")

class FinancialDataRequest(BaseModel):
    stock_code: str = Field(..., description="Stock code (e.g., '000001', '600036') for pytdx financial data")
    report_date: str = Field(..., description="Reporting date in YYYY-MM-DD format (e.g., '2023-09-30')")

class FuturesHistRequest(BaseModel):
    symbol: str = Field(..., description="Futures contract symbol (e.g., 'RB0', 'if2401')")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    period: str = Field(default='daily', description="Data period ('daily', '1min', '5min', '15min', '30min', '60min')")
    market_exchange: Optional[str] = Field(default=None, description="Market exchange (e.g., 'SHFE', 'CFFEX') for specific daily contracts")
