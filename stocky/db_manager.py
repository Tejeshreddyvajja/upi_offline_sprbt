"""
PostgreSQL Database Manager for Stock Data
Handles connection, table creation, and data operations
"""
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from datetime import datetime
import os

# Database connection parameters
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "stocky"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "1234"),
}


def get_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise


def create_tables():
    """Create necessary tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Create stock_data table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stock_data (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(10) NOT NULL,
                date DATE NOT NULL,
                open FLOAT,
                high FLOAT,
                low FLOAT,
                close FLOAT,
                volume BIGINT,
                daily_return FLOAT,
                sma_20 FLOAT,
                sma_50 FLOAT,
                ema_20 FLOAT,
                rsi FLOAT,
                volatility_20 FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, date)
            );
        """)
        
        # Create index for faster queries
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_ticker_date 
            ON stock_data (ticker, date DESC);
        """)
        
        # Create predictions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(10) NOT NULL,
                date DATE NOT NULL,
                prediction INT,
                confidence FLOAT,
                trend VARCHAR(20),
                rsi_signal VARCHAR(20),
                risk_level VARCHAR(20),
                position_size FLOAT,
                decision VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        print("[OK] Tables created successfully")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating tables: {e}")
    finally:
        cur.close()
        conn.close()


def insert_stock_data(ticker, df):
    """Insert stock data into the database."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        data = []
        for _, row in df.iterrows():
            data.append((
                ticker,
                row["Date"],
                row.get("Open"),
                row.get("High"),
                row.get("Low"),
                row["Close"],
                row.get("Volume"),
                row.get("Daily_Return"),
                row.get("SMA_20"),
                row.get("SMA_50"),
                row.get("EMA_20"),
                row.get("RSI"),
                row.get("Volatility_20"),
            ))
        
        # Use ON CONFLICT to update existing records
        execute_values(
            cur,
            """
            INSERT INTO stock_data 
            (ticker, date, open, high, low, close, volume, daily_return, 
             sma_20, sma_50, ema_20, rsi, volatility_20)
            VALUES %s
            ON CONFLICT (ticker, date) 
            DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume,
                daily_return = EXCLUDED.daily_return,
                sma_20 = EXCLUDED.sma_20,
                sma_50 = EXCLUDED.sma_50,
                ema_20 = EXCLUDED.ema_20,
                rsi = EXCLUDED.rsi,
                volatility_20 = EXCLUDED.volatility_20;
            """,
            data,
            page_size=500
        )
        
        conn.commit()
        print(f"[OK] Inserted {len(data)} rows for {ticker}")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error inserting data: {e}")
    finally:
        cur.close()
        conn.close()


def get_stock_data(ticker, start_date, end_date=None):
    """Retrieve stock data from database."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        if end_date is None:
            end_date = datetime.now().date()
        
        cur.execute("""
            SELECT date, open, high, low, close, volume, daily_return,
                   sma_20, sma_50, ema_20, rsi, volatility_20
            FROM stock_data
            WHERE ticker = %s AND date BETWEEN %s AND %s
            ORDER BY date ASC;
        """, (ticker, start_date, end_date))
        
        rows = cur.fetchall()
        if rows:
            df = pd.DataFrame(
                rows,
                columns=[
                    "Date", "Open", "High", "Low", "Close", "Volume",
                    "Daily_Return", "SMA_20", "SMA_50", "EMA_20", "RSI", "Volatility_20"
                ]
            )
            df["Date"] = pd.to_datetime(df["Date"])
            return df
        return None
    except Exception as e:
        print(f"[ERROR] Error retrieving data: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def insert_prediction(ticker, date, prediction_data):
    """Store prediction results."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO predictions
            (ticker, date, prediction, confidence, trend, rsi_signal, risk_level, position_size, decision)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            ticker,
            date,
            prediction_data.get("prediction"),
            prediction_data.get("confidence"),
            prediction_data.get("trend"),
            prediction_data.get("rsi_signal"),
            prediction_data.get("risk_level"),
            prediction_data.get("position_size"),
            prediction_data.get("decision"),
        ))
        
        conn.commit()
        print(f"[OK] Prediction stored for {ticker}")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error storing prediction: {e}")
    finally:
        cur.close()
        conn.close()


def get_latest_prediction(ticker):
    """Get the latest prediction for a ticker."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT * FROM predictions
            WHERE ticker = %s
            ORDER BY date DESC
            LIMIT 1;
        """, (ticker,))
        
        row = cur.fetchone()
        return row
    except Exception as e:
        print(f"[ERROR] Error retrieving prediction: {e}")
        return None
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    # Initialize database
    print("Initializing database...")
    create_tables()
    print("[OK] Database initialized successfully!")
