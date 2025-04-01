# src/sentiment.py

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd

# Ensure VADER lexicon is downloaded (only needs to run once per environment)
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except nltk.downloader.DownloadError:
    print("VADER lexicon not found. Downloading...")
    nltk.download('vader_lexicon')
except LookupError:
     print("VADER lexicon lookup failed. Downloading...")
     nltk.download('vader_lexicon')


# Initialize the analyzer globally to avoid reloading it repeatedly
try:
    analyzer = SentimentIntensityAnalyzer()
    print("VADER Sentiment Analyzer initialized.")
except Exception as e:
    print(f"Error initializing VADER Analyzer: {e}")
    analyzer = None

def analyze_sentiment(text):
    """
    Analyzes the sentiment of a single text string using VADER.

    Args:
        text (str): The text to analyze.

    Returns:
        float: The compound sentiment score (-1 to 1), or np.nan if analyzer failed.
               Returns 0.0 if text is empty or None.
    """
    if not text:
        return 0.0
    if analyzer is None:
        print("VADER Analyzer not available.")
        return pd.NA # Use pandas NA for missing numeric

    try:
        vs = analyzer.polarity_scores(text)
        return vs['compound']
    except Exception as e:
        print(f"Error during sentiment analysis for text '{text[:50]}...': {e}")
        return pd.NA


def get_daily_sentiment(headlines_data):
    """
    Calculates the average daily sentiment score from a list of headlines.

    Args:
        headlines_data (list): A list of dictionaries, each with 'datetime' and 'headline'.

    Returns:
        pd.Series: A Series with date (index) and average compound sentiment score (values).
                   Returns empty Series if input is empty or analysis fails.
    """
    if not headlines_data:
        return pd.Series(dtype=float)

    df = pd.DataFrame(headlines_data)
    if 'datetime' not in df.columns or 'headline' not in df.columns:
         print("Error: headlines_data format incorrect.")
         return pd.Series(dtype=float)

    df['date'] = df['datetime'].dt.date # Extract just the date part
    df['sentiment_score'] = df['headline'].apply(analyze_sentiment)

    # Drop rows where sentiment analysis failed
    df.dropna(subset=['sentiment_score'], inplace=True)
    if df.empty:
        print("No valid sentiment scores could be calculated.")
        return pd.Series(dtype=float)

    # Calculate the mean sentiment score for each day
    daily_sentiment = df.groupby('date')['sentiment_score'].mean()

    print(f"Calculated daily sentiment for {len(daily_sentiment)} days.")
    return daily_sentiment