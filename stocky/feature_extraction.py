import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Get ticker from command line or use default
stock_symbol = sys.argv[1].upper() if len(sys.argv) > 1 else "AAPL"

print(f"Extracting features for {stock_symbol}...")

input_file = f"data/{stock_symbol}_stock_data_cleaned.csv"
if not Path(input_file).exists():
    print(f"Error: {input_file} not found. Run clean.py first.")
    sys.exit(1)

df = pd.read_csv(input_file)
df['Date'] = pd.to_datetime(df['Date'])
df['Daily_Return'] = df['Close'].pct_change()

# Simple Moving Averages
df['SMA_20'] = df['Close'].rolling(window=20).mean()
df['SMA_50'] = df['Close'].rolling(window=50).mean()

# Exponential Moving Average
df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()

# RSI Calculation
delta = df['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
df['RSI'] = 100 - (100 / (1 + rs))

df['Volatility_20'] = df['Daily_Return'].rolling(window=20).std()
df.dropna(inplace=True)
df.reset_index(drop=True, inplace=True)

output_file = f"data/{stock_symbol}_features.csv"
df.to_csv(output_file, index=False)
print(f"[OK] Feature extraction completed and saved to {output_file}")
