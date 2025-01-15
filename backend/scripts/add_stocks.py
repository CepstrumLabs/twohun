import requests
import argparse
from typing import List

def add_stock(ticker: str, days: int = 7, base_url: str = "http://localhost:8000") -> None:
    """Add historical data for a single stock."""
    url = f"{base_url}/api/stocks/{ticker}"
    try:
        response = requests.post(url, params={"days": days})
        response.raise_for_status()
        result = response.json()
        print(f"Success: {result['message']}")
    except requests.exceptions.RequestException as e:
        print(f"Error adding {ticker}: {str(e)}")

def add_multiple_stocks(tickers: List[str], days: int = 7, base_url: str = "http://localhost:8000") -> None:
    """Add historical data for multiple stocks."""
    for ticker in tickers:
        add_stock(ticker, days, base_url)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add historical stock data to the database")
    parser.add_argument("tickers", nargs="+", help="One or more stock tickers (e.g., AAPL MSFT GOOGL)")
    parser.add_argument("--days", type=int, default=7, help="Number of days of historical data to fetch")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    
    args = parser.parse_args()
    add_multiple_stocks(args.tickers, args.days, args.url) 