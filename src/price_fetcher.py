# src/price_fetcher.py

import yfinance as yf
import pandas as pd

def get_stock_data(ticker, start_date, end_date):
    """
    Fetches historical stock data (Adjusted Close) using yfinance.

    Args:
        ticker (str): The stock ticker symbol.
        start_date (str or datetime): Start date for historical data.
        end_date (str or datetime): End date for historical data.

    Returns:
        pd.DataFrame: DataFrame with dates as index and 'Adj Close' column.
                      Returns empty DataFrame on error.
    """
    print(f"Fetching price data for {ticker} from {start_date} to {end_date}...")
    try:
        stock = yf.Ticker(ticker)
        # Add one day to end_date for yfinance inclusiveness if needed
        # end_date_yf = pd.to_datetime(end_date) + pd.Timedelta(days=1)
        hist = stock.history(start=start_date, end=end_date, auto_adjust=True) # auto_adjust handles Adj Close

        if hist.empty:
            print(f"No price data found for {ticker} in the specified period.")
            return pd.DataFrame()

        # Keep only the closing price (yfinance auto_adjust=True names it 'Close')
        # Rename it to 'Adj Close' for consistency if needed, but 'Close' is fine if auto_adjust=True
        price_df = hist[['Close']].copy()
        price_df.rename(columns={'Close': 'adj_close'}, inplace=True) # Rename for consistency
        price_df.index = price_df.index.date # Use date only, drop time component

        print(f"Fetched {len(price_df)} price data points for {ticker}.")
        return price_df

    except Exception as e:
        print(f"Error fetching price data for {ticker}: {e}")
        return pd.DataFrame()