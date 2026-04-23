"""
Collect data for all popular stocks and save to PostgreSQL
"""
import subprocess
import sys

stocks = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX",
    "ADBE", "INTC", "AMD", "CSCO", "ORCL", "CRM", "IBM",
    "JPM", "GS", "V", "MA", "PYPL", "BAC",
    "WMT", "KO", "PEP", "NKE", "DIS", "MCD", "SBUX",
    "BA", "F", "GM", "XOM", "CVR", "PFE", "JNJ", "MRNA"
]

print(f"Collecting data for {len(stocks)} stocks...")
print("=" * 60)

failed = []
for i, stock in enumerate(stocks, 1):
    print(f"\n[{i}/{len(stocks)}] Processing {stock}...")
    try:
        result = subprocess.run(
            [sys.executable, "run_pipeline.py", stock],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print(f"  [OK] {stock} completed")
        else:
            print(f"  [ERROR] {stock} failed")
            failed.append(stock)
    except Exception as e:
        print(f"  [ERROR] {stock}: {e}")
        failed.append(stock)

print("\n" + "=" * 60)
print(f"Collection completed!")
print(f"Successful: {len(stocks) - len(failed)}/{len(stocks)}")
if failed:
    print(f"Failed: {', '.join(failed)}")
