"""Migrate data from postgres to stocky database"""
import psycopg2
import pandas as pd

print("Migrating data from postgres to stocky database...")

# Connect to postgres database to get the data
print("Connecting to postgres database...")
conn_postgres = psycopg2.connect(host="127.0.0.1", port="5432", database="postgres", user="postgres", password="1234")

# Read stock_data from postgres
print("Reading stock_data from postgres...")
df_stock_data = pd.read_sql("SELECT * FROM stock_data;", conn_postgres)
print(f"Found {len(df_stock_data)} rows in stock_data")

# Read predictions from postgres
print("Reading predictions from postgres...")
df_predictions = pd.read_sql("SELECT * FROM predictions;", conn_postgres)
print(f"Found {len(df_predictions)} rows in predictions")

conn_postgres.close()

# Connect to stocky database to insert the data
print("\nConnecting to stocky database...")
conn_stocky = psycopg2.connect(host="127.0.0.1", port="5432", database="stocky", user="postgres", password="1234")
cur_stocky = conn_stocky.cursor()

try:
    # Insert stock_data
    print("Inserting stock_data into stocky database...")
    for _, row in df_stock_data.iterrows():
        cur_stocky.execute("""
            INSERT INTO stock_data (ticker, date, open, high, low, close, volume, daily_return, sma_20, sma_50, ema_20, rsi, volatility_20, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticker, date) DO NOTHING;
        """, (
            row['ticker'], row['date'], row['open'], row['high'], row['low'], 
            row['close'], row['volume'], row['daily_return'], row['sma_20'], 
            row['sma_50'], row['ema_20'], row['rsi'], row['volatility_20'], row['created_at']
        ))
    
    conn_stocky.commit()
    print(f"[OK] Inserted {len(df_stock_data)} rows into stock_data")
    
    # Insert predictions if any
    if len(df_predictions) > 0:
        print("Inserting predictions into stocky database...")
        for _, row in df_predictions.iterrows():
            cur_stocky.execute("""
                INSERT INTO predictions (ticker, date, prediction, confidence, trend, rsi_signal, risk_level, position_size, decision, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                row['ticker'], row['date'], row['prediction'], row['confidence'],
                row['trend'], row['rsi_signal'], row['risk_level'], row['position_size'],
                row['decision'], row['created_at']
            ))
        conn_stocky.commit()
        print(f"[OK] Inserted {len(df_predictions)} rows into predictions")
    
    print("\n[OK] Data migration completed successfully!")
    
except Exception as e:
    conn_stocky.rollback()
    print(f"Error during migration: {e}")
finally:
    cur_stocky.close()
    conn_stocky.close()
