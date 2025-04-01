# Financial News Sentiment Analysis Pipeline

This project scrapes financial news headlines, performs sentiment analysis, fetches corresponding stock prices, stores the combined data in a PostgreSQL database, and analyzes the correlation between news sentiment and subsequent stock price movements.

## Features

*   Scrapes headlines for specified tickers from Finviz.com.
*   Uses NLTK's VADER for sentiment analysis on news headlines.
*   Fetches historical adjusted closing prices using `yfinance`.
*   Stores ticker, date, adjusted close price, and average daily sentiment score in a PostgreSQL database.
*   Provides basic correlation analysis between lagged sentiment scores and future price percentage changes.
*   Generates plots comparing sentiment trends and price movements per ticker.
*   Configurable tickers, date ranges (implicitly via news), database credentials, and analysis parameters.

## Project Structure

```
financial-news-sentiment-analyzer/
|-- src/                      # Source code module
|   |-- __init__.py
|   |-- config.py             # Database & scraper configuration (MODIFY THIS)
|   |-- database.py           # Functions for database interactions
|   |-- scraper.py            # Functions for scraping news headlines (Finviz)
|   |-- sentiment.py          # Functions for sentiment analysis (VADER)
|   |-- price_fetcher.py      # Functions for fetching stock prices (yfinance)
|   |-- analysis.py           # Functions for correlation analysis
|-- notebooks/                # Optional: For exploratory analysis
|   `-- exploration.ipynb     # Example notebook placeholder
|-- sentiment_analysis_results/ # Output folder for plots (created automatically)
|-- .gitignore
|-- run_pipeline.py         # Main script to execute the workflow
|-- requirements.txt
|-- setup_db.sql            # SQL script to initialize the database table
`-- README.md                 # This file
```

## Setup

1.  **Prerequisites:**
    *   **Python 3.7+**
    *   **PostgreSQL Server:** You need a running PostgreSQL instance. Install it from [postgresql.org](https://www.postgresql.org/download/).
    *   **Git** (Optional, for cloning)

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/RajaBabu15/financial-news-sentiment-analyzer.git
    cd financial-news-sentiment-analyzer
    ```

3.  **Create a Database:**
    *   Connect to your PostgreSQL server (e.g., using `psql` or a GUI like pgAdmin).
    *   Create a new database. The default name used in `config.py` is `sentiment_db`.
        ```sql
        CREATE DATABASE sentiment_db;
        ```
    *   Ensure you have a user role with privileges to connect, create tables, and insert/select data in this database.

4.  **Configure Database Credentials:**
    *   **IMPORTANT:** Open `src/config.py`.
    *   Update the `DB_CONFIG` dictionary with your actual PostgreSQL database name, username, password, host, and port.
    *   **Do NOT commit `config.py` with your real credentials to public repositories.** Add it to your `.gitignore` if you modify it locally. Consider using environment variables for production setups.

5.  **Create Virtual Environment & Install Dependencies:**
    ```bash
    python -m venv venv
    # Activate:
    # Windows: venv\Scripts\activate
    # macOS/Linux: source venv/bin/activate

    pip install -r requirements.txt
    ```

6.  **Download NLTK Data:** The first time `src/sentiment.py` runs, it will attempt to download the 'vader_lexicon' if it's not found. You might need an internet connection then. Alternatively, run this once manually in a Python interpreter after activating the venv:
    ```python
    import nltk
    nltk.download('vader_lexicon')
    ```

7.  **Setup Database Table:** The main script `run_pipeline.py` will automatically execute the `setup_db.sql` script to create the necessary table (`financial_sentiment`) if it doesn't exist. Ensure your database user has permission to create tables.

## Running the Pipeline

1.  **Configure Tickers & Parameters (Optional):**
    *   Open `run_pipeline.py`.
    *   Modify the `TICKERS_TO_PROCESS` list with the stock symbols you want to analyze.
    *   Adjust `SENTIMENT_LAG_DAYS` and `PRICE_CHANGE_DAYS` in `src/config.py` if you want to explore different correlation lags.

2.  **Execute the Pipeline:**
    *   Make sure your PostgreSQL server is running.
    *   Run the main script from the project's root directory:
    ```bash
    python run_pipeline.py
    ```

## Output

1.  **Console Logs:** Status messages detailing the process for each ticker (scraping, sentiment analysis, price fetching, database insertion), correlation results per ticker, and total execution time.
2.  **Database:** The `financial_sentiment` table in your specified PostgreSQL database will be populated with the combined ticker, date, adjusted close price, and average daily sentiment score. Data is inserted using an "upsert" logic (ON CONFLICT DO UPDATE), so running the pipeline again for the same tickers might update existing entries.
3.  **Plots:** PNG plots comparing the adjusted close price and sentiment scores (daily and 7-day rolling average) for each processed ticker will be saved in the `sentiment_analysis_results/` directory.

## Disclaimer

*   **Educational Use:** This project is intended for educational purposes to demonstrate web scraping, sentiment analysis, data storage, and basic correlation analysis.
*   **No Investment Advice:** The results (especially correlation) are preliminary insights and **do not constitute financial advice**. Sentiment is just one factor among many influencing stock prices.
*   **Scraping Ethics:** Web scraping should be done responsibly. The script includes a small delay (`SCRAPER_DELAY`), but frequent, aggressive scraping can lead to IP bans. Always check Finviz's `robots.txt` and terms of service. The structure of websites can change, breaking the scraper.
*   **VADER Limitations:** VADER is good for general sentiment but may not capture financial nuances perfectly. More sophisticated NLP models could be used.
*   **Correlation vs. Causation:** Correlation analysis shows statistical relationships but does not prove causation. Many other factors affect stock prices.
*   **Data Quality:** Relies on the accuracy of data from Finviz and yfinance.

# Setup and Running:

1.  **Install PostgreSQL:** Make sure it's installed and running.
2.  **Create Database:** Create a database named `sentiment_db` (or update `config.py`). Create a user/role that can access it.
3.  **Update `src/config.py`:** **Crucially, put your real database credentials here.**
4.  **Create Environment & Install:**
    ```bash
    cd financial-news-sentiment-analyzer
    python -m venv venv
    # Activate (use appropriate command for your OS)
    source venv/bin/activate # Linux/macOS
    # venv\Scripts\activate # Windows
    pip install -r requirements.txt
    ```
5.  **Run the Pipeline:**
    ```bash
    python run_pipeline.py
    ```

The script will then execute the steps, print logs, populate the database, and save plots to the `sentiment_analysis_results` folder.