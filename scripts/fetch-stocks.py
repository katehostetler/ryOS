#!/usr/bin/env python3
"""
Fetch daily stock prices for AI-related companies using yfinance.
Outputs to data/pressure/stocks.json
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import yfinance as yf

# Stock tickers for AI companies and their investors
TICKERS = {
    "MSFT": "Microsoft",    # OpenAI investor
    "GOOGL": "Alphabet",    # Anthropic investor + DeepMind
    "AMZN": "Amazon",       # Anthropic investor
    "META": "Meta",         # Meta AI direct
    "NVDA": "NVIDIA",       # Industry bellwether
}

def fetch_stock_data():
    """Fetch current stock data and recent history for all tickers."""
    stocks = []

    for ticker, name in TICKERS.items():
        try:
            stock = yf.Ticker(ticker)

            # Get last 30 days of history for sparkline
            hist = stock.history(period="1mo")

            if hist.empty:
                print(f"Warning: No data for {ticker}")
                continue

            # Get latest price and calculate change
            latest = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) > 1 else hist.iloc[0]

            price = round(latest['Close'], 2)
            change = round(price - prev['Close'], 2)
            change_percent = round((change / prev['Close']) * 100, 2)

            # Extract closing prices for history (last 30 days)
            history = [round(p, 2) for p in hist['Close'].tolist()]

            stocks.append({
                "ticker": ticker,
                "name": name,
                "price": price,
                "change": change,
                "changePercent": change_percent,
                "history": history[-30:],  # Last 30 days
            })

            print(f"Fetched {ticker}: ${price} ({change_percent:+.2f}%)")

        except Exception as e:
            print(f"Error fetching {ticker}: {e}")

    return stocks

def main():
    """Main function to fetch and save stock data."""
    # Determine output path (works both locally and in GitHub Actions)
    script_dir = Path(__file__).parent.parent
    output_path = script_dir / "data" / "pressure" / "stocks.json"

    print(f"Fetching stock data...")
    stocks = fetch_stock_data()

    data = {
        "lastUpdated": datetime.utcnow().isoformat() + "Z",
        "stocks": stocks,
    }

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to file
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Saved stock data to {output_path}")

if __name__ == "__main__":
    main()
