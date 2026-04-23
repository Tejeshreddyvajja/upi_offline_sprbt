# Automatic Stock Data Updates - Setup Guide

## Python Scheduler (APScheduler)

Your stock data can now update **automatically every day at 4 AM** (after market closes).

### Quick Start

#### Option 1: Run Once (Testing)

To test the scheduler before setting it up permanently:

```bash
python scheduler.py
```

This will start the scheduler and wait for the scheduled time. Press `Ctrl+C` to stop.

---

#### Option 2: Run as Background Service (Windows)

**Step 1: Create a batch file**

Create a file named `start_scheduler.bat` in your stocky folder:

```batch
@echo off
cd C:\Users\SURESH\Desktop\stocky
.venv\Scripts\python.exe scheduler.py
pause
```

**Step 2: Schedule with Windows Task Scheduler**

1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click **Create Basic Task** (right side)
3. Fill in:
   - **Name:** "Update Stock Data"
   - **Description:** "Daily stock data collection at 4 AM"
4. Click **Next**
5. Select **Daily** → Click **Next**
6. Set time to **4:00 AM** → Click **Next**
7. Select **Start a program** → Click **Next**
8. Browse and select your `start_scheduler.bat` file
9. Click **Finish**

Now the scheduler will run automatically each day at 4 AM!

---

### Monitoring

**Check the logs:**

```bash
type stock_update.log
```

This shows all update history and any errors.

**Recent logs:**

```bash
Get-Content stock_update.log -Tail 20  # Last 20 lines
```

---

### Dashboard Updates

The dashboard now shows:
- **Last Updated:** Timestamp of the most recent data in the database
- When you refresh the page, it will display the latest data automatically

---

### Manual Updates (Anytime)

You can still run updates manually:

```bash
python collect_all_stocks.py
```

This updates all 36 stocks immediately without waiting for the scheduled time.

---

### How It Works

1. **Runs at 4 AM** - After market closes
2. **Collects data** for all 36 stocks from Yahoo Finance
3. **Processes data** - cleans and extracts technical indicators
4. **Saves to PostgreSQL** - updates the database
5. **Logs results** - records success/failures in `stock_update.log`

---

### Troubleshooting

**Scheduler not running?**
- Check Windows Task Scheduler (search "Task Scheduler")
- Verify `start_scheduler.bat` path is correct
- Check `stock_update.log` for errors

**Data not updating?**
- Manual test: `python collect_all_stocks.py`
- Check internet connection (needs Yahoo Finance access)
- Verify PostgreSQL is running: `python check_db.py`

**Wrong update time?**
Edit `scheduler.py` line 57:
```python
schedule.every().day.at("04:00").do(update_all_stocks)  # Change "04:00" to desired time
```

---

### Statistics

- **Stocks tracked:** 36
- **Records per update:** ~72,000 total
- **Update frequency:** Daily at 4 AM
- **Data retention:** All historical data preserved in PostgreSQL
