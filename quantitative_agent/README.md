# Personal Quantitative Investment Agent

This project aims to provide tools and strategies for quantitative investment analysis.

## Project Structure

-   `quantitative_agent/src/`: Contains the source code for data fetching, feature engineering, strategy development, etc.
-   `quantitative_agent/data/`: Intended for storing downloaded data, processed features, etc. (currently not used by data_fetcher.py directly for saving).
-   `quantitative_agent/tests/`: Contains unit tests for the source code.
-   `quantitative_agent/api/`: Contains the FastAPI application for exposing functionalities.

## Data Fetching

The primary way to get financial data into this system is through the functions provided in `quantitative_agent/src/data_fetcher.py`.

### Using `yfinance` for Global Market Data
(Content as before)
...

### Using `pytdx` for A-Share OHLCV Data (China Market)
(Content as before)
...

### Fetching A-Share Financial Data (`pytdx.crawler`)
(Content as before)
...

### Fetching Chinese Futures Market Data (AkShare)
(Content as before)
...

## API Usage

This section details how to run the API server and interact with its endpoints.

### Running the API Server

**Prerequisites:**
Ensure the necessary Python packages are installed. From the project root (`quantitative_agent` parent directory):
```bash
pip install fastapi uvicorn pandas requests yfinance pytdx akshare
```
(Note: `pandas` and `requests` are generally good to have, specific data fetchers have their own deps like `yfinance`, `pytdx`, `akshare` which should be installed by their respective `pip install` commands if not already covered by the main project dependencies.)

**Command to Start the Server:**
Navigate to the project root directory (the parent directory of `quantitative_agent`) and run:
```bash
uvicorn quantitative_agent.api.main:app --reload --host 0.0.0.0 --port 8000
```
-   `uvicorn`: The ASGI server.
-   `quantitative_agent.api.main:app`: Points to the `app` instance in your `quantitative_agent/api/main.py` file.
-   `--reload`: Enables auto-reloading on code changes (useful for development).
-   `--host 0.0.0.0`: Makes the server accessible on your network.
-   `--port 8000`: Specifies the port.

Once running, the API provides interactive documentation:
-   **Swagger UI**: `http://localhost:8000/docs`
-   **ReDoc**: `http://localhost:8000/redoc`

### Available Endpoints

#### Stock Data

Endpoints related to stock market data (OHLCV, financials).

##### Endpoint: `POST /stocks/ohlcv/yfinance/`

Fetches historical Open, High, Low, Close, and Volume (OHLCV) data from Yahoo Finance.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "start_date": "2023-01-01",
  "end_date": "2023-01-10"
}
```

**Example with `curl`:**
```bash
curl -X POST "http://localhost:8000/stocks/ohlcv/yfinance/" \
-H "Content-Type: application/json" \
-d '{
  "symbol": "AAPL",
  "start_date": "2023-01-01",
  "end_date": "2023-01-10"
}'
```

**Example with Python `requests`:**
```python
import requests
import json

url = "http://localhost:8000/stocks/ohlcv/yfinance/"
payload = {
  "symbol": "AAPL",
  "start_date": "2023-01-01",
  "end_date": "2023-01-10"
}
response = requests.post(url, json=payload)

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")
```

**Response:**
A JSON array of objects, where each object represents a trading day's OHLCV data. Dates are in 'YYYY-MM-DD' format.
```json
[
  {
    "Date": "2023-01-03",
    "Open": 128.61,
    "High": 129.22,
    "Low": 122.58,
    "Close": 123.47,
    "Volume": 112117500
  },
  { ... }
]
```

##### Endpoint: `POST /stocks/ohlcv/pytdx/`

Fetches historical OHLCV data for Chinese A-shares using `pytdx`.

**Request Body:**
```json
{
  "stock_code": "000001",
  "start_date": "2023-01-01",
  "end_date": "2023-01-10"
}
```

**Example with `curl`:**
```bash
curl -X POST "http://localhost:8000/stocks/ohlcv/pytdx/" \
-H "Content-Type: application/json" \
-d '{
  "stock_code": "000001",
  "start_date": "2023-01-01",
  "end_date": "2023-01-10"
}'
```

**Example with Python `requests`:**
```python
import requests
import json

url = "http://localhost:8000/stocks/ohlcv/pytdx/"
payload = {
  "stock_code": "000001",
  "start_date": "2023-01-01",
  "end_date": "2023-01-10"
}
response = requests.post(url, json=payload)

if response.status_code == 200:
    data = response.json()
    # Use ensure_ascii=False if stock names/info might contain Chinese characters
    print(json.dumps(data, indent=2, ensure_ascii=False))
else:
    print(f"Error: {response.status_code} - {response.text}")
```

**Response:**
A JSON array of objects, where each object represents a trading day's OHLCV data. Dates are in 'YYYY-MM-DD HH:MM:SS' format.
```json
[
  {
    "Date": "2023-01-03 15:00:00",
    "Open": 13.20,
    "High": 13.85,
    "Low": 13.05,
    "Close": 13.77,
    "Volume": 2194128.0
  },
  { ... }
]
```

##### Endpoint: `POST /stocks/financials/pytdx/`

Fetches historical financial statement data for a Chinese A-share stock for a specific reporting period, using `pytdx.crawler`.

**Request Body:**
```json
{
  "stock_code": "000001",
  "report_date": "2023-06-30"
}
```
(Note: Ensure the `report_date` corresponds to an actual financial reporting period like "YYYY-03-31", "YYYY-06-30", "YYYY-09-30", "YYYY-12-31" for which data is available on TDX servers.)

**Example with `curl`:**
```bash
curl -X POST "http://localhost:8000/stocks/financials/pytdx/" \
-H "Content-Type: application/json" \
-d '{
  "stock_code": "000001",
  "report_date": "2023-06-30"
}'
```

**Example with Python `requests`:**
```python
import requests
import json

url = "http://localhost:8000/stocks/financials/pytdx/"
payload = {
  "stock_code": "000001",
  "report_date": "2023-06-30"
}
response = requests.post(url, json=payload)

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
else:
    print(f"Error: {response.status_code} - {response.text}")
```

**Response:**
A JSON array containing a single object if the stock data is found. The object's `code` field (from the original DataFrame index) will be the stock code. Columns are generically named `col1`, `col2`, etc., along with a `report_date` column from the data file.
```json
[
  {
    "code": "000001",
    "report_date": "2023-06-30",
    "col1": 1.23,
    "col2": 4.56,
    // ... more 'colX' fields ...
  }
]
```
**Important**: To interpret `colX` fields, refer to external TDX documentation or financial data dictionaries (e.g., from QUANTAXIS `financial_mean.py`).

#### Futures Data

Endpoints related to futures market data.

##### Endpoint: `POST /futures/history/akshare/`

Fetches historical futures data (daily or intraday) for Chinese markets using `AkShare`.

**Request Body Examples:**

*   For daily main continuous contract (e.g., Rebar Steel "RB0"):
    ```json
    {
      "symbol": "RB0",
      "start_date": "2023-12-01",
      "end_date": "2023-12-10",
      "period": "daily"
    }
    ```
*   For a specific daily contract (e.g., Gold "au2412" from SHFE):
    ```json
    {
      "symbol": "au2412",
      "start_date": "2023-12-01",
      "end_date": "2023-12-10",
      "period": "daily",
      "market_exchange": "SHFE"
    }
    ```
*   For 1-minute intraday data (e.g., CSI 300 Index Future "IF0"; dates are often ignored for latest day):
    ```json
    {
      "symbol": "IF0",
      "start_date": "2024-06-21",
      "end_date": "2024-06-21",
      "period": "1min"
    }
    ```

**Example with `curl` (using daily main continuous):**
```bash
curl -X POST "http://localhost:8000/futures/history/akshare/" \
-H "Content-Type: application/json" \
-d '{
  "symbol": "RB0",
  "start_date": "2023-12-01",
  "end_date": "2023-12-10",
  "period": "daily"
}'
```

**Example with Python `requests` (using specific daily contract):**
```python
import requests
import json

url = "http://localhost:8000/futures/history/akshare/"
payload = {
  "symbol": "au2412",
  "start_date": "2023-12-01",
  "end_date": "2023-12-10",
  "period": "daily",
  "market_exchange": "SHFE"
}
response = requests.post(url, json=payload)

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
else:
    print(f"Error: {response.status_code} - {response.text}")
```

**Response:**
A JSON array of objects, where each object represents a data point (daily bar or intraday tick). Includes 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', and optionally 'OpenInterest' and 'Settlement'. Date format varies ('YYYY-MM-DD' for daily, 'YYYY-MM-DD HH:MM:SS' for intraday).
```json
[
  {
    "Date": "2023-12-01", // or "2023-12-01 09:01:00" for intraday
    "Open": 3900.0,
    "High": 3950.0,
    // ... other fields ...
  },
  { ... }
]
```
