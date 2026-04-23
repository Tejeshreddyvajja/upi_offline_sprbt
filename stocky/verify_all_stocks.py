"""Verify all stocks are in the database"""
from db_manager import get_connection

conn = get_connection()
cur = conn.cursor()

# Get all unique tickers and their record counts
cur.execute("""
    SELECT ticker, COUNT(*) as record_count 
    FROM stock_data 
    GROUP BY ticker 
    ORDER BY ticker;
""")

results = cur.fetchall()

print(f"\nTotal Tickers in Database: {len(results)}")
print("=" * 50)
print(f"{'Ticker':<8} {'Records':<10}")
print("=" * 50)

total_records = 0
for ticker, count in results:
    print(f"{ticker:<8} {count:<10}")
    total_records += count

print("=" * 50)
print(f"{'TOTAL':<8} {total_records:<10}")
print("=" * 50)

cur.close()
conn.close()
