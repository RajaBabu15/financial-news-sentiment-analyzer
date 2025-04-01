# src/scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
from src.config import SCRAPER_HEADERS, SCRAPER_DELAY

def scrape_finviz_headlines(ticker):
    """
    Scrapes news headlines for a given ticker from Finviz.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        list: A list of dictionaries, each containing 'datetime' (datetime object)
              and 'headline' (str). Returns empty list on error.
    """
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    headlines = []
    last_date_str = None # To handle rows without explicit dates

    print(f"Scraping Finviz for {ticker}...")
    try:
        response = requests.get(url, headers=SCRAPER_HEADERS)
        response.raise_for_status() # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')
        news_table = soup.find(id='news-table')

        if not news_table:
            print(f"Could not find news table for {ticker}.")
            return []

        for row in news_table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) == 2:
                date_time_str = cells[0].text.strip()
                headline_text = cells[1].a.text.strip() if cells[1].a else cells[1].text.strip()

                # Try parsing datetime - Finviz format can be "Mon-DD-YY HH:MM AM/PM" or just "HH:MM AM/PM"
                try:
                    # Check if it contains date and time
                    if ' ' in date_time_str and '-' in date_time_str:
                         dt_object = datetime.strptime(date_time_str, '%b-%d-%y %I:%M%p')
                         last_date_str = dt_object.strftime('%b-%d-%y') # Store the date part
                    # Check if it only contains time (use last seen date)
                    elif ':' in date_time_str and last_date_str:
                        full_dt_str = f"{last_date_str} {date_time_str}"
                        dt_object = datetime.strptime(full_dt_str, '%b-%d-%y %I:%M%p')
                    else:
                         # Skip if format is unexpected or no date context yet
                         # print(f"Skipping row with unparsable date/time: {date_time_str}")
                         continue

                    headlines.append({'datetime': dt_object, 'headline': headline_text})

                except ValueError as date_err:
                    # print(f"Could not parse date/time '{date_time_str}': {date_err}")
                    continue # Skip row if parsing fails

        print(f"Found {len(headlines)} headlines for {ticker}.")
        time.sleep(SCRAPER_DELAY) # Be polite
        return headlines

    except requests.exceptions.RequestException as e:
        print(f"Error during request for {ticker}: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during scraping for {ticker}: {e}")
        return []