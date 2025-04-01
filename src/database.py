# src/database.py

import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import pandas as pd
from src.config import DB_CONFIG

def connect_db():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Database connection successful.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        print("Please ensure PostgreSQL is running and configuration in src/config.py is correct.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during DB connection: {e}")
        return None


def execute_sql_file(conn, filepath):
    """Executes SQL commands from a file."""
    try:
        with conn.cursor() as cur:
            with open(filepath, 'r') as f:
                sql_commands = f.read()
                cur.execute(sql_commands)
        conn.commit()
        print(f"Successfully executed SQL from {filepath}")
        return True
    except Exception as e:
        print(f"Error executing SQL file {filepath}: {e}")
        conn.rollback() # Rollback changes on error
        return False


def insert_sentiment_data(conn, data_df):
    """
    Inserts or updates sentiment and price data into the database.

    Args:
        conn: Active psycopg2 database connection.
        data_df (pd.DataFrame): DataFrame with columns
                                  ['ticker', 'date', 'adj_close', 'sentiment_score'].
                                  'date' should be datetime.date objects.
    """
    if data_df is None or data_df.empty:
        print("No data provided for insertion.")
        return

    table_name = 'financial_sentiment'
    cols = ['ticker', 'date', 'adj_close', 'sentiment_score']

    # Ensure DataFrame has the correct columns
    if not all(col in data_df.columns for col in cols):
        print(f"Error: DataFrame missing required columns. Expected: {cols}")
        return

    # Prepare data tuples, ensuring date is just date (not datetime)
    data_tuples = [tuple(x) for x in data_df[cols].to_numpy()]

    insert_query = sql.SQL("""
        INSERT INTO {} ({})
        VALUES %s
        ON CONFLICT (ticker, date) DO UPDATE SET
          adj_close = EXCLUDED.adj_close,
          sentiment_score = EXCLUDED.sentiment_score;
    """).format(
        sql.Identifier(table_name),
        sql.SQL(', ').join(map(sql.Identifier, cols))
    )

    try:
        with conn.cursor() as cur:
            execute_values(cur, insert_query, data_tuples)
        conn.commit()
        print(f"Successfully inserted/updated {len(data_tuples)} rows into {table_name}.")
    except Exception as e:
        print(f"Error inserting data into {table_name}: {e}")
        conn.rollback()


def fetch_data_for_analysis(conn, tickers=None, start_date=None, end_date=None):
    """
    Fetches combined sentiment and price data from the database for analysis.

    Args:
        conn: Active psycopg2 database connection.
        tickers (list, optional): List of tickers to fetch. Defaults to all.
        start_date (str or datetime.date, optional): Start date.
        end_date (str or datetime.date, optional): End date.

    Returns:
        pd.DataFrame: DataFrame with fetched data, sorted by ticker and date.
                      Returns empty DataFrame on error or no data.
    """
    table_name = 'financial_sentiment'
    query = sql.SQL("SELECT ticker, date, adj_close, sentiment_score FROM {}").format(sql.Identifier(table_name))
    conditions = []
    params = []

    if tickers:
        conditions.append(sql.SQL("ticker = ANY(%s)"))
        params.append(tickers)
    if start_date:
        conditions.append(sql.SQL("date >= %s"))
        params.append(start_date)
    if end_date:
        conditions.append(sql.SQL("date <= %s"))
        params.append(end_date)

    if conditions:
        query += sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions)

    query += sql.SQL(" ORDER BY ticker, date;")

    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
        if not rows:
            print("No data found matching the criteria.")
            return pd.DataFrame(columns=colnames)

        df = pd.DataFrame(rows, columns=colnames)
        df['date'] = pd.to_datetime(df['date']) # Ensure date is datetime object
        print(f"Successfully fetched {len(df)} rows for analysis.")
        return df

    except Exception as e:
        print(f"Error fetching data from {table_name}: {e}")
        return pd.DataFrame() # Return empty DataFrame on error