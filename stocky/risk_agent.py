import pandas as pd
import numpy as np


def risk_level(vol):
    if vol < 0.01:
        return "Low Risk"
    elif vol < 0.02:
        return "Medium Risk"
    else:
        return "High Risk"


def position_size(vol):
    if vol < 0.01:
        return 1.0   # Full position
    elif vol < 0.02:
        return 0.5   # Half position
    else:
        return 0.25  # Small position


def run_risk_analysis(df):
    """Analyze risk based on volatility."""
    latest_vol = df['Volatility_20'].iloc[-1]
    latest_price = df['Close'].iloc[-1]
    
    risk_status = risk_level(latest_vol)
    stop_loss_pct = latest_vol * 2
    stop_loss_price = latest_price * (1 - stop_loss_pct)
    position = position_size(latest_vol)
    
    return {
        "Risk_Level": risk_status,
        "Latest_Volatility": round(latest_vol, 5),
        "Suggested_Stop_Loss": round(stop_loss_price, 2),
        "Position_Size": position
    }


if __name__ == "__main__":
    df = pd.read_csv("data/AAPL_features.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    risk_output = run_risk_analysis(df)
    print(risk_output)
