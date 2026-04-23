# PostgreSQL Setup Guide for Stocky

## Installation

### Windows:
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer and follow the steps
3. Remember the password you set for the `postgres` user
4. Add PostgreSQL to PATH (installer usually does this)

### Mac:
```bash
brew install postgresql@15
brew services start postgresql@15
```

### Linux (Ubuntu/Debian):
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

## Database Setup

### 1. Create Database and User

Open PostgreSQL command line (psql):

```bash
# On Windows: Open psql from Start Menu
# On Mac/Linux:
psql -U postgres
```

Then run these commands:

```sql
-- Create database
CREATE DATABASE stocky;

-- Create user (optional, or use postgres)
CREATE USER stocky_user WITH PASSWORD 'stocky_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE stocky TO stocky_user;
```

Exit psql with: `\q`

### 2. Configure Environment Variables

Create a `.env` file in your stocky directory:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stocky
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

Or modify directly in `db_manager.py` (default values already set to use `postgres` user).

### 3. Initialize Database Tables

Run this once to create tables:

```bash
python db_manager.py
```

You should see: `✅ Database initialized successfully!`

## Connection Test

```bash
python -c "from db_manager import get_connection; get_connection(); print('Connected!')"
```

## Usage in Dashboard

The dashboard now:
- Stores all stock data in PostgreSQL
- Persists data across sessions
- No more in-memory caching
- Retrieves historical data from database when available

## Troubleshooting

**Connection refused?**
- Check if PostgreSQL is running
- On Windows: Services > PostgreSQL > Start
- On Mac: `brew services start postgresql@15`

**Password error?**
- Update `.env` file with correct password
- Or modify DB_PASSWORD in `db_manager.py`

**Permission denied?**
- Make sure user has database privileges: `GRANT ALL PRIVILEGES ON DATABASE stocky TO user_name;`

## Next Steps

1. Run: `python db_manager.py`
2. Restart dashboard: `streamlit run dashboard.py`
3. Dashboard now uses PostgreSQL for persistent storage!
