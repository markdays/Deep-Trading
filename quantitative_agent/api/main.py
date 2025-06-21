from fastapi import FastAPI
from . import stocks_router
from . import futures_router # Import futures_router

app = FastAPI(title="Quantitative Investment Agent API")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Quantitative Investment Agent API"}

# Include stock-related routes (OHLCV, Financials)
app.include_router(stocks_router.router, prefix="/stocks", tags=["Stock Data"])
# Include futures-related routes
app.include_router(futures_router.router, prefix="/futures", tags=["Futures Data"])
