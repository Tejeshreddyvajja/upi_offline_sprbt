import yfinance as yf
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
from db_manager import insert_stock_data, create_tables

# Get ticker from command line or use default
stock_symbol = sys.argv[1].upper() if len(sys.argv) > 1 else "AAPL"

print(f"Collecting data for {stock_symbol}...")

# Initialize database
try:
    create_tables()
except:
    pass  # Tables might already exist

# Fetch data up to today
today = datetime.now().strftime("%Y-%m-%d")
data = yf.download(stock_symbol, start="2018-01-01", end=today)
data.columns = data.columns.get_level_values(0)
data.reset_index(inplace=True)

# Create data directory if it doesn't exist
Path("data").mkdir(exist_ok=True)

# Save to CSV
output_file = f"data/{stock_symbol}_stock_data.csv"
data.to_csv(output_file, index=False)
print(f"[OK] Data saved to CSV: {output_file}")

# Save to PostgreSQL
try:
    insert_stock_data(stock_symbol, data)
    print(f"[OK] Data saved to PostgreSQL")
except Exception as e:
    print(f"[WARNING] Could not save to PostgreSQL: {e}")
    print("    Make sure PostgreSQL is running and configured in db_manager.py")
