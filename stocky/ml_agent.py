import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras import Input
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping


def _build_sequences(features, targets, sequence_length, split_index):
    """Create rolling sequences and split them into train/validation sets."""
    x_train, y_train, x_val, y_val = [], [], [], []

    for i in range(sequence_length, len(features)):
        sequence = features[i - sequence_length:i]
        label = targets[i]

        if i < split_index:
            x_train.append(sequence)
            y_train.append(label)
        else:
            x_val.append(sequence)
            y_val.append(label)

    return (
        np.array(x_train, dtype=np.float32),
        np.array(y_train, dtype=np.float32),
        np.array(x_val, dtype=np.float32),
        np.array(y_val, dtype=np.float32),
    )


def run_ml_prediction(df):
    """Train an LSTM model and predict next-day direction on latest data."""
    tf.random.set_seed(42)
    np.random.seed(42)

    features = [
        'Daily_Return',
        'SMA_20',
        'SMA_50',
        'EMA_20',
        'RSI',
        'Volatility_20'
    ]

    required_columns = set(features + ['Close'])
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for LSTM model: {missing}")

    df_model = df.copy()
    df_model.dropna(subset=features + ['Close'], inplace=True)

    if len(df_model) < 40:
        raise ValueError("Not enough rows to train LSTM model. Need at least 40 clean rows.")

    # Keep the newest row for inference only, because it has no known next-day target.
    supervised_df = df_model.iloc[:-1].copy()
    supervised_df['Target'] = (
        df_model['Close'].shift(-1).iloc[:-1].values > supervised_df['Close'].values
    ).astype(int)

    sequence_length = 20
    split = int(len(supervised_df) * 0.8)
    split = max(sequence_length + 1, split)
    split = min(split, len(supervised_df) - 1)

    scaler = MinMaxScaler()
    train_features = supervised_df[features].iloc[:split]
    scaler.fit(train_features)

    scaled_supervised = scaler.transform(supervised_df[features])
    y = supervised_df['Target'].to_numpy(dtype=np.float32)

    X_train, y_train, X_val, y_val = _build_sequences(
        scaled_supervised,
        y,
        sequence_length,
        split
    )

    if len(X_train) == 0:
        raise ValueError("Unable to create training sequences. Add more historical data.")

    model = Sequential([
        Input(shape=(sequence_length, len(features))),
        LSTM(32, return_sequences=True),
        Dropout(0.2),
        LSTM(16),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    fit_kwargs = {
        'x': X_train,
        'y': y_train,
        'epochs': 25,
        'batch_size': 16,
        'verbose': 0,
        'callbacks': [EarlyStopping(monitor='val_loss', patience=4, restore_best_weights=True)]
    }

    if len(X_val) > 0:
        fit_kwargs['validation_data'] = (X_val, y_val)
    else:
        fit_kwargs['validation_split'] = 0.2

    model.fit(**fit_kwargs)

    latest_window = df_model[features].iloc[-sequence_length:]
    if len(latest_window) < sequence_length:
        raise ValueError("Not enough rows to build latest prediction window for LSTM.")

    latest_scaled = scaler.transform(latest_window)
    latest_sequence = np.expand_dims(latest_scaled, axis=0)

    probability_up = float(model.predict(latest_sequence, verbose=0)[0][0])
    prediction = int(probability_up >= 0.5)
    confidence = probability_up if prediction == 1 else (1.0 - probability_up)

    return {
        "Prediction": prediction,
        "Confidence": float(confidence)
    }


if __name__ == "__main__":
    df = pd.read_csv("data/AAPL_features.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    ml_output = run_ml_prediction(df)
    print("Model Accuracy and Prediction:", ml_output)
