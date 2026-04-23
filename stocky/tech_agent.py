import pandas as pd


def detect_trend(row):
    if row['SMA_20'] > row['SMA_50']:
        return "Bullish"
    elif row['SMA_20'] < row['SMA_50']:
        return "Bearish"
    else:
        return "Neutral"


def rsi_signal(rsi):
    if rsi > 70:
        return "Overbought"
    elif rsi < 30:
        return "Oversold"
    else:
        return "Normal"


def run_technical_analysis(df):
    """Run technical analysis on a dataframe with features."""
    latest = df.iloc[-1]
    trend = detect_trend(latest)
    rsi_status = rsi_signal(latest['RSI'])
    
    return {
        "Trend": trend,
        "RSI_Signal": rsi_status,
        "SMA_20": round(latest['SMA_20'], 2),
        "SMA_50": round(latest['SMA_50'], 2),
        "RSI": round(latest['RSI'], 2)
    }


if __name__ == "__main__":
    from pathlib import Path
    data_dir = Path(__file__).resolve().parent / "data"
    df = pd.read_csv(data_dir / "AAPL_features.csv")
    technical_output = run_technical_analysis(df)
    print(technical_output)

