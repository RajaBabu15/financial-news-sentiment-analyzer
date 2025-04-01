# src/config.py

# -- PostgreSQL Database Configuration --
# !! IMPORTANT: Replace with your actual database credentials !!
# Consider using environment variables for better security in a real application.
DB_CONFIG = {
    "database": "sentiment_db",  # Name of the database you create
    "user": "your_db_user",      # Your PostgreSQL username
    "password": "your_db_password",# Your PostgreSQL password
    "host": "localhost",         # Or your DB host if not local
    "port": "5432"               # Default PostgreSQL port
}

# -- Scraping Configuration --
# Finviz requires a User-Agent header to avoid being blocked
SCRAPER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
# Add a small delay between requests to be polite to the server
SCRAPER_DELAY = 1 # seconds

# -- Analysis Configuration --
# Lag sentiment by how many days to correlate with price changes
SENTIMENT_LAG_DAYS = 1
# Calculate price change over how many days
PRICE_CHANGE_DAYS = 1