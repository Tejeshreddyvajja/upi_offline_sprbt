import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import subprocess
import os
import sys

# Import agent functions
from tech_agent import run_technical_analysis
from ml_agent import run_ml_prediction
from risk_agent import run_risk_analysis
from decision_agent import make_final_decision
from db_manager import get_stock_data, get_connection

st.set_page_config(page_title="Agentic AI Stock Analysis", page_icon="📈", layout="wide")

def get_last_update_time():
    """Get the timestamp of the most recent data in the database"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT MAX(created_at) FROM stock_data;")
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result and result[0]:
            return result[0]
    except:
        pass
    return None

try:
    # =================================
    # SIDEBAR — USER INPUT
    # =================================
    st.sidebar.title("⚙️ Settings")
    
    stock_list = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX",
        "ADBE", "INTC", "AMD", "CSCO", "ORCL", "CRM", "IBM",
        "JPM", "GS", "V", "MA", "PYPL", "BAC",
        "WMT", "KO", "PEP", "NKE", "DIS", "MCD", "SBUX",
        "BA", "F", "GM", "XOM", "CVR", "PFE", "JNJ", "MRNA"
    ]
    
    ticker = st.sidebar.selectbox("Select Stock", stock_list, index=0)
    ticker_input = st.sidebar.text_input("Or Enter Custom Symbol", ticker)
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Refresh Data"):
        with st.spinner("Refreshing stock data for all tracked symbols..."):
            venv_python = os.path.join(".venv", "Scripts", "python.exe")
            if not os.path.exists(venv_python):
                venv_python = sys.executable

            result = subprocess.run(
                [venv_python, "collect_all_stocks.py"],
                capture_output=True,
                text=True
            )

            logs = result.stdout or ""
            if result.stderr:
                logs = f"{logs}\n{result.stderr}" if logs else result.stderr
            st.session_state["collection_logs"] = logs.strip() or "No logs were produced."

            if result.returncode == 0:
                st.success("Stock data refreshed successfully.")
            else:
                st.error("Stock data refresh failed.")
                st.code(st.session_state["collection_logs"])

        st.rerun()
    
    # Use custom ticker if provided
    ticker_parts = [part for part in ticker_input.replace(",", " ").split() if part]
    if not ticker_parts:
        st.error("Please enter a ticker symbol.")
        st.stop()
    ticker = ticker_parts[0].upper()
    
    # =================================
    # DATA LOADING FROM POSTGRESQL
    # =================================
    def load_data_from_db(symbol, start_dt):
        # Query database for stock data (no caching - always fetch fresh)
        df = get_stock_data(symbol, start_dt, datetime.now().date())
        
        if df is None or df.empty:
            return None
        
        # Ensure Date column is datetime
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)
        
        return df

    # ======================
    # LOAD DATA FROM DATABASE
    # ======================
    df = load_data_from_db(ticker, datetime(2018, 1, 1).date())
    
    if df is None or df.empty:
        st.error(f"No data found for {ticker} in database. Run the pipeline first: python run_pipeline.py {ticker}")
        st.stop()

    # Data features should already be in the database
    # But recalculate them if missing for robustness
    if "Daily_Return" not in df.columns or df["Daily_Return"].isna().all():
        df["Daily_Return"] = df["Close"].pct_change()
    
    if "SMA_20" not in df.columns or df["SMA_20"].isna().all():
        df["SMA_20"] = df["Close"].rolling(20).mean()
    
    if "SMA_50" not in df.columns or df["SMA_50"].isna().all():
        df["SMA_50"] = df["Close"].rolling(50).mean()
    
    if "EMA_20" not in df.columns or df["EMA_20"].isna().all():
        df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
    
    if "RSI" not in df.columns or df["RSI"].isna().all():
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))
    
    if "Volatility_20" not in df.columns or df["Volatility_20"].isna().all():
        df["Volatility_20"] = df["Daily_Return"].rolling(20).std()

    df_features = df.dropna().copy()
    
    if df_features.empty:
        st.error(f"Not enough data to compute indicators. Try an earlier start date.")
        st.stop()

    # ======================
    # RUN ALL AGENTS
    # ======================
    technical_output = run_technical_analysis(df_features)
    ml_output = run_ml_prediction(df_features)
    risk_output = run_risk_analysis(df_features)
    final_output = make_final_decision(technical_output, ml_output, risk_output)
    
    decision = final_output["Decision"]
    trend = technical_output["Trend"]
    rsi_status = technical_output["RSI_Signal"]
    confidence = ml_output["Confidence"]
    risk_status = risk_output["Risk_Level"]
    position = risk_output["Position_Size"]
    
    # Get latest price and prediction
    latest = df_features.iloc[-1]
    latest_date = latest["Date"].date()
    latest_price = latest["Close"]
    volatility = latest["Volatility_20"]
    
    # Predict tomorrow's price range based on ML prediction and volatility
    prediction = ml_output["Prediction"]
    if prediction == 1:  # Price expected to go UP
        predicted_change = volatility * latest_price  # Expected move
        predicted_price = latest_price + predicted_change
        direction = "↗️ UP"
        delta_value = f"+${predicted_change:.2f} ({confidence*100:.0f}% confident)"
    else:  # Price expected to go DOWN
        predicted_change = volatility * latest_price
        predicted_price = latest_price - predicted_change
        direction = "↘️ DOWN"
        delta_value = f"-${predicted_change:.2f} ({confidence*100:.0f}% confident)"

    # =================================
    # UI HEADER
    # =================================
    st.title("📊 Agentic AI Stock Analysis Dashboard")
    
    # Display last update time
    last_update = get_last_update_time()
    if last_update:
        st.caption(f"Live Analysis for: **{ticker}** | Last Updated: **{last_update.strftime('%Y-%m-%d %H:%M:%S')}**")
    else:
        st.caption(f"Live Analysis for: **{ticker}**")

    if st.session_state.get("collection_logs"):
        with st.expander("📜 Latest Collection Logs", expanded=False):
            st.code(st.session_state["collection_logs"], language="text")
    
    # =================================
    # PRICE INFORMATION
    # =================================
    st.subheader("💰 Price Information")
    
    price_col1, price_col2, price_col3 = st.columns(3)
    
    with price_col1:
        st.metric("Latest Date", str(latest_date))
    
    with price_col2:
        st.metric("Current Price", f"${latest_price:.2f}")
    
    with price_col3:
        st.metric(
            "Tomorrow's Prediction",
            f"${predicted_price:.2f}",
            delta=delta_value
        )
    
    st.caption(f"*Prediction based on ML model with {confidence*100:.0f}% confidence. Estimated range uses volatility.")
    
    st.markdown("---")

    # =================================
    # DECISION DISPLAY (COLOR BADGE)
    # =================================
    if decision == "BUY":
        st.success(f"🟢 FINAL DECISION: **{decision}**")
    elif decision == "AVOID":
        st.error(f"🔴 FINAL DECISION: **{decision}**")
    else:
        st.warning(f"🟡 FINAL DECISION: **{decision}**")

    # =================================
    # METRICS PANEL
    # =================================
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Trend", trend)
    c2.metric("RSI Status", rsi_status)
    c3.metric("Risk Level", risk_status)
    c4.metric("ML Confidence", f"{round(confidence, 2)}")

    st.markdown("**Position Size:**")
    st.progress(position)
    st.caption(f"{int(position * 100)}% of portfolio")

    st.markdown("---")

    # Show more details
    with st.expander("📊 Technical Details"):
        st.json(technical_output)
    
    with st.expander("🤖 ML Details"):
        st.json(ml_output)
    
    with st.expander("⚠️ Risk Details"):
        st.json(risk_output)

    # =================================
    # CHARTS
    # =================================
    st.subheader("📈 Price & Moving Averages")

    chart_df = df.set_index("Date")[["Close", "SMA_20", "SMA_50"]]
    st.line_chart(chart_df)

    st.subheader("📉 RSI Indicator")

    rsi_df = df.set_index("Date")[["RSI"]]
    st.line_chart(rsi_df)

except Exception as exc:
    st.exception(exc)
