# run_pipeline.py

import pandas as pd
from datetime import date, timedelta
import os
import time

from src.database import connect_db, execute_sql_file, insert_sentiment_data, fetch_data_for_analysis
from src.scraper import scrape_finviz_headlines
from src.sentiment import get_daily_sentiment
from src.price_fetcher import get_stock_data
from src.analysis import calculate_sentiment_price_correlation, plot_sentiment_vs_price
from src.config import SENTIMENT_LAG_DAYS, PRICE_CHANGE_DAYS

# --- Configuration ---
# List of tickers to process
TICKERS_TO_PROCESS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

# Date range for fetching price data (adjust as needed)
# Go back far enough to cover news history scraped by Finviz + buffer
END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=90) # Fetch ~3 months of price data

# Output directory for plots
OUTPUT_DIR = 'sentiment_analysis_results'

# --- Main Pipeline ---
if __name__ == "__main__":
    print("--- Financial Sentiment Analysis Pipeline ---")
    start_pipeline_time = time.time()

    # Create output directory
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. Connect to Database and Setup Table
    conn = connect_db()
    if conn is None:
        print("Exiting pipeline due to database connection failure.")
        exit()

    print("\nSetting up database table...")
    if not execute_sql_file(conn, 'setup_db.sql'):
        print("Exiting pipeline due to database setup failure.")
        conn.close()
        exit()

    all_processed_data = []

    # 2. Process Each Ticker
    for ticker in TICKERS_TO_PROCESS:
        print(f"\n--- Processing Ticker: {ticker} ---")
        ticker_start_time = time.time()

        # Scrape Headlines
        headlines = scrape_finviz_headlines(ticker)
        if not headlines:
            print(f"No headlines found for {ticker}, skipping.")
            continue

        # Calculate Daily Sentiment
        daily_sentiment = get_daily_sentiment(headlines)
        if daily_sentiment.empty:
            print(f"Could not calculate sentiment for {ticker}, skipping.")
            continue

        # Get date range from sentiment data
        min_sentiment_date = daily_sentiment.index.min()
        max_sentiment_date = daily_sentiment.index.max()
        print(f"Sentiment data range: {min_sentiment_date} to {max_sentiment_date}")

        # Adjust price fetch range based on sentiment data found
        price_start_date = min_sentiment_date
        price_end_date = max_sentiment_date # Fetch up to the last sentiment day

        # Fetch Price Data
        price_data = get_stock_data(ticker, start_date=price_start_date, end_date=price_end_date)
        if price_data.empty:
            print(f"Could not fetch price data for {ticker}, skipping.")
            continue

        # Combine Sentiment and Price Data
        # Convert daily_sentiment Series to DataFrame for merging
        sentiment_df = daily_sentiment.reset_index()
        sentiment_df.rename(columns={'index': 'date', 0: 'sentiment_score'}, inplace=True)
        sentiment_df['date'] = pd.to_datetime(sentiment_df['date']).dt.date # Ensure it's date object

        # Merge requires index alignment or common column - use date
        # Reset index on price_data if date is index
        if isinstance(price_data.index, pd.DatetimeIndex) or isinstance(price_data.index, pd.Index) and price_data.index.name == 'date':
             price_data = price_data.reset_index()
        # Ensure price_data 'date' is date object
        price_data['date'] = pd.to_datetime(price_data['date']).dt.date


        # Perform merge on the 'date' column
        combined_df = pd.merge(price_data, sentiment_df, on='date', how='inner') # Inner join keeps only dates with both price and sentiment
        combined_df['ticker'] = ticker # Add ticker column

        if combined_df.empty:
            print(f"No overlapping dates found between price and sentiment data for {ticker}.")
            continue

        print(f"Combined data for {ticker}: {len(combined_df)} rows")

        # Insert Combined Data into Database
        insert_sentiment_data(conn, combined_df[['ticker', 'date', 'adj_close', 'sentiment_score']])

        all_processed_data.append(combined_df) # Keep data for later analysis

        ticker_end_time = time.time()
        print(f"Finished processing {ticker} in {ticker_end_time - ticker_start_time:.2f} seconds.")

    # 3. Perform Overall Analysis (after processing all tickers)
    if not all_processed_data:
        print("\nNo data was processed for any ticker. Cannot perform analysis.")
    else:
        print("\n--- Performing Correlation Analysis ---")
        # Combine all dataframes from the list
        analysis_df = pd.concat(all_processed_data, ignore_index=True)
        analysis_df = analysis_df.sort_values(by=['ticker', 'date'])

        # Calculate correlation per ticker
        correlation_per_ticker = calculate_sentiment_price_correlation(
            analysis_df,
            sentiment_lag=SENTIMENT_LAG_DAYS,
            price_change_lag=PRICE_CHANGE_DAYS,
            group_by_ticker=True
        )
        print("\nCorrelation (Lagged Sentiment vs Price Change) per Ticker:")
        if not correlation_per_ticker.empty:
            print(correlation_per_ticker.to_string(float_format='{:.4f}'.format))
        else:
            print("Could not calculate correlation per ticker.")


        # Calculate overall correlation (optional, might be less meaningful)
        # overall_correlation = calculate_sentiment_price_correlation(
        #     analysis_df,
        #     sentiment_lag=SENTIMENT_LAG_DAYS,
        #     price_change_lag=PRICE_CHANGE_DAYS,
        #     group_by_ticker=False
        # )
        # print(f"\nOverall Correlation (across all tickers): {overall_correlation:.4f if pd.notna(overall_correlation) else 'N/A'}")


        # 4. Generate Plots per Ticker
        print("\n--- Generating Plots ---")
        for ticker in analysis_df['ticker'].unique():
             plot_sentiment_vs_price(analysis_df, ticker, output_dir=OUTPUT_DIR)


    # 5. Close Database Connection
    if conn:
        conn.close()
        print("\nDatabase connection closed.")

    end_pipeline_time = time.time()
    print(f"\n--- Pipeline Finished in {end_pipeline_time - start_pipeline_time:.2f} seconds ---")