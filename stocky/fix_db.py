"""Migrate tables from postgres database to stocky database"""
import psycopg2

# Step 1: Check what's in stocky database
print("Checking stocky database...")
conn_stocky = psycopg2.connect(host="127.0.0.1", port="5432", database="stocky", user="postgres", password="1234")
cur_stocky = conn_stocky.cursor()
cur_stocky.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
tables_in_stocky = cur_stocky.fetchall()
print(f"Tables in stocky: {tables_in_stocky}")
cur_stocky.close()
conn_stocky.close()

# Step 2: Update db_manager to use stocky
print("\nUpdating db_manager.py configuration...")
with open('db_manager.py', 'r') as f:
    content = f.read()

# Replace the default database from postgres to stocky
old_line = '"database": os.getenv("DB_NAME", "postgres"),'
new_line = '"database": os.getenv("DB_NAME", "stocky"),'

if old_line in content:
    content = content.replace(old_line, new_line)
    with open('db_manager.py', 'w') as f:
        f.write(content)
    print("[OK] Updated db_manager.py - database default changed to 'stocky'")
else:
    print("[ERROR] Could not find the line to replace")

print("\nNow run: python db_manager.py")
print("This will create tables in the stocky database.")
