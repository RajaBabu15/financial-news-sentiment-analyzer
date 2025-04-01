# src/analysis.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def calculate_sentiment_price_correlation(df, sentiment_lag=1, price_change_lag=1, group_by_ticker=True):
    """
    Calculates correlation between lagged sentiment and future price changes.

    Args:
        df (pd.DataFrame): DataFrame containing 'ticker', 'date', 'adj_close', 'sentiment_score'.
                           Must be sorted by ticker (if applicable) and date.
        sentiment_lag (int): Number of days to lag the sentiment score.
        price_change_lag (int): Number of days over which to calculate price change.
        group_by_ticker (bool): Whether to calculate correlation per ticker or overall.

    Returns:
        float or pd.Series: Pearson correlation coefficient(s).
                             Series indexed by ticker if group_by_ticker is True.
                             NaN if calculation fails.
    """
    if df is None or df.empty:
        print("Cannot calculate correlation on empty DataFrame.")
        return np.nan if not group_by_ticker else pd.Series(dtype=float)

    required_cols = ['date', 'adj_close', 'sentiment_score']
    if group_by_ticker:
        required_cols.append('ticker')

    if not all(col in df.columns for col in required_cols):
        print(f"Error: DataFrame missing required columns for correlation. Expected: {required_cols}")
        return np.nan if not group_by_ticker else pd.Series(dtype=float)

    print(f"\nCalculating correlation: Lagged Sentiment ({sentiment_lag}d) vs Price Change ({price_change_lag}d)...")

    # Ensure data is sorted for correct shifting and pct_change
    df = df.sort_values(by=['ticker', 'date'] if group_by_ticker else ['date']).copy()

    if group_by_ticker:
        # Calculate within each ticker group
        df['price_change'] = df.groupby('ticker')['adj_close'].pct_change(periods=price_change_lag)
        df['sentiment_lagged'] = df.groupby('ticker')['sentiment_score'].shift(sentiment_lag)

        # Calculate correlation per ticker
        correlation_results = df.groupby('ticker')[['sentiment_lagged', 'price_change']].corr(method='pearson')
        # Extract the specific correlation value
        correlations = correlation_results.unstack().loc[:, ('sentiment_lagged', 'price_change')]

        print("Correlation calculated per ticker.")
        return correlations

    else:
        # Calculate overall
        df['price_change'] = df['adj_close'].pct_change(periods=price_change_lag)
        df['sentiment_lagged'] = df['sentiment_score'].shift(sentiment_lag)

        # Drop NaNs introduced by shifting/pct_change before calculating correlation
        df_cleaned = df.dropna(subset=['sentiment_lagged', 'price_change'])

        if df_cleaned.empty or len(df_cleaned) < 2:
            print("Not enough valid data points after lagging/differencing for overall correlation.")
            return np.nan

        correlation = df_cleaned['sentiment_lagged'].corr(df_cleaned['price_change'], method='pearson')
        print(f"Overall correlation calculated: {correlation:.4f}")
        return correlation


def plot_sentiment_vs_price(df, ticker, output_dir='.'):
    """Creates a simple plot of sentiment vs adjusted close price for a ticker."""
    if df is None or df.empty:
        print(f"No data to plot for {ticker}.")
        return

    ticker_df = df[df['ticker'] == ticker].set_index('date')
    if ticker_df.empty:
        print(f"No data found for ticker {ticker} in the DataFrame.")
        return

    fig, ax1 = plt.subplots(figsize=(15, 7))

    color = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Adj Close Price', color=color)
    ax1.plot(ticker_df.index, ticker_df['adj_close'], color=color, label='Adj Close')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, axis='y', linestyle=':', alpha=0.6)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:red'
    ax2.set_ylabel('Avg Daily Sentiment Score', color=color)
    # Plot sentiment, maybe add rolling average for smoothing
    ax2.plot(ticker_df.index, ticker_df['sentiment_score'], color=color, alpha=0.6, label='Daily Sentiment')
    # Optional: Add rolling average
    rolling_sent = ticker_df['sentiment_score'].rolling(window=7, min_periods=3).mean()
    ax2.plot(rolling_sent.index, rolling_sent, color='tab:orange', linestyle='--', label='Sentiment (7d Avg)')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(-1, 1) # VADER compound score range

    fig.suptitle(f'{ticker} - Adjusted Close Price vs. Daily Sentiment', fontsize=16)
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9)) # Combine legends
    fig.autofmt_xdate()
    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to prevent title overlap

    # Save plot
    plot_filename = os.path.join(output_dir, f"{ticker}_sentiment_vs_price.png")
    try:
        plt.savefig(plot_filename, dpi=150)
        print(f"Plot saved to {plot_filename}")
        plt.close(fig)
    except Exception as e:
        print(f"Error saving plot {plot_filename}: {e}")
        plt.show()