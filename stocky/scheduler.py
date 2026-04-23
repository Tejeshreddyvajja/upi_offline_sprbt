"""
Automatic daily stock data updater using APScheduler
Runs data collection every day at 4 AM (after market closes)
"""
import schedule
import time
import subprocess
import sys
import os
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    filename='stock_update.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def update_all_stocks():
    """Run the data collection pipeline for all stocks"""
    print(f"\n{'='*60}")
    print(f"Starting automatic stock data update: {datetime.now()}")
    print(f"{'='*60}\n")
    logging.info("Starting automatic stock data update")
    
    venv_python = os.path.join(".venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        venv_python = sys.executable
    
    try:
        result = subprocess.run(
            [venv_python, "collect_all_stocks.py"],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        if result.returncode == 0:
            print("[OK] Stock data update completed successfully!")
            logging.info("Stock data update completed successfully")
        else:
            print(f"[ERROR] Update failed:\n{result.stderr}")
            logging.error(f"Update failed: {result.stderr}")
    
    except subprocess.TimeoutExpired:
        print("[ERROR] Update timed out after 1 hour")
        logging.error("Update timed out")
    except Exception as e:
        print(f"[ERROR] Update failed: {e}")
        logging.error(f"Update failed: {e}")
    
    print(f"\n{'='*60}")
    print(f"Update finished: {datetime.now()}")
    print(f"{'='*60}\n")

def start_scheduler():
    """Start the scheduler"""
    print("\n" + "="*60)
    print("Stock Data Scheduler Started")
    print("="*60)
    print(f"Current time: {datetime.now()}")
    print("Schedule: Daily at 04:00 AM")
    print("="*60 + "\n")
    
    logging.info("Scheduler started")
    
    # Schedule the update to run every day at 4 AM
    schedule.every().day.at("04:00").do(update_all_stocks)
    
    print("Waiting for scheduled time...\n")
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        start_scheduler()
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")
        logging.info("Scheduler stopped by user")
        sys.exit(0)
