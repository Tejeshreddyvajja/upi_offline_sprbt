"""Check which database and tables exist"""
from db_manager import DB_CONFIG, get_connection

print('DATABASE CONFIG:')
print(f'Database: {DB_CONFIG["database"]}')
print(f'Host: {DB_CONFIG["host"]}')
print(f'User: {DB_CONFIG["user"]}')

try:
    conn = get_connection()
    cur = conn.cursor()
    
    # List all databases
    cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
    databases = cur.fetchall()
    print(f'\nAvailable Databases:')
    for db in databases:
        print(f'  - {db[0]}')
    
    # List tables in current database
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
    tables = cur.fetchall()
    print(f'\nTables in "{DB_CONFIG["database"]}":')
    if tables:
        for table in tables:
            print(f'  - {table[0]}')
            # Get row count
            cur.execute(f"SELECT COUNT(*) FROM {table[0]};")
            count = cur.fetchone()[0]
            print(f'    ({count} rows)')
    else:
        print('  (none found)')
    
    cur.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
