import pandas as pd
import sys
from pathlib import Path

# Get ticker from command line or use default
stock_symbol = sys.argv[1].upper() if len(sys.argv) > 1 else "AAPL"

print(f"Cleaning data for {stock_symbol}...")

input_file = f"data/{stock_symbol}_stock_data.csv"
if not Path(input_file).exists():
    print(f"Error: {input_file} not found. Run collect.py first.")
    sys.exit(1)

df = pd.read_csv(input_file)
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')
df.reset_index(drop=True, inplace=True)
df.isnull().sum()
df.ffill(inplace=True)
df.drop(columns=['Adj Close'], inplace=True, errors='ignore')

output_file = f"data/{stock_symbol}_stock_data_cleaned.csv"
df.to_csv(output_file, index=False)
print(f"[OK] Cleaned data saved to {output_file}")