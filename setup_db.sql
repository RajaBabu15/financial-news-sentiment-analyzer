-- setup_db.sql

-- Drop table if it exists (optional, be careful in production)
-- DROP TABLE IF EXISTS financial_sentiment;

-- Create the main table to store sentiment and price data
CREATE TABLE IF NOT EXISTS financial_sentiment (
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    adj_close NUMERIC(12, 4),         -- Adjusted closing price
    sentiment_score NUMERIC(7, 6),    -- VADER compound score (-1 to 1)
    PRIMARY KEY (ticker, date)        -- Ensure uniqueness per ticker per day
);

-- Optional: Add indexes for faster querying
CREATE INDEX IF NOT EXISTS idx_financial_sentiment_ticker ON financial_sentiment (ticker);
CREATE INDEX IF NOT EXISTS idx_financial_sentiment_date ON financial_sentiment (date);

-- Grant permissions if needed (replace 'your_db_user' with the actual user from config.py)
-- GRANT ALL PRIVILEGES ON TABLE financial_sentiment TO your_db_user;
-- GRANT USAGE, SELECT ON SEQUENCE (if any sequences are used) TO your_db_user;

-- Display message on completion
\echo 'Database table financial_sentiment setup complete (if no errors).'