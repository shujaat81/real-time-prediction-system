import json
import time
import numpy as np
import joblib
import sys

from kafka import KafkaConsumer
from tensorflow.keras.models import load_model

from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.producer.kafka_producer import create_producer
from data.processed.process_csv_data import FEATURES

# Kafka Configuration
KAFKA_BROKER = "localhost:9092"
INPUT_TOPIC = "stock-input-data-topic"
OUTPUT_TOPIC = "stock-prediction-data-topic"

# Load trained model, scaler, and label encoder
model = load_model("nifty50_lstm_model.h5", compile=False)
scaler = joblib.load("scaler.pkl")
scaler_close = joblib.load("scaler_close.pkl")
label_encoder = joblib.load("label_encoder.pkl")


# Initialize Kafka Consumer
def create_consumer():
    return KafkaConsumer(
        INPUT_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
    )


def preprocess_message(df_stock, message):
    """Prepares the last 10 days of stock data for prediction"""
    symbol = message["symbol"]
    close_price = message["close_price"]
    open_price = message["open_price"]
    high_price = message["high_price"]
    low_price = message["low_price"]
    volume = message["volume"]

    # Store last 10 days of stock data
    stock_history = df_stock[df_stock["Symbol"] == symbol].tail(10)
    print(stock_history)

    stock_prices = stock_history[FEATURES].values

    print(f"stock_prices: {stock_prices}")

    # stock_prices = np.append(stock_prices, [open_price, high_price, low_price, close_price, volume])

    if len(stock_prices) < 10:
        return None  # Wait for 10 days of data

    stock_prices = np.array(stock_prices, dtype=np.float32)

    # Scale input data properly
    scaled_input = scaler.transform(stock_prices)
    input_data = np.array(scaled_input, dtype=np.float32).reshape(1, 10, 5)

    return input_data


def start_consumer():
    consumer = create_consumer()
    print("Consumer started... Listening for messages...")

    for message in consumer:
        print(f"Received message: {message}")
        stock_data = message.value
        symbol = stock_data["symbol"]
        date = stock_data["date"]

        print(f"Received data for {symbol} on {date}: {stock_data}")

        # Preprocess the input
        input_data = preprocess_message(stock_data)

        if input_data is None:
            continue

        # Predict next day price
        predicted_price = model.predict(input_data)[0][0]

        # Denormalize the predicted price
        predicted_price = scaler_close.inverse_transform(
            [[0, 0, 0, predicted_price, 0]]
        )[0][3]

        # Create output message
        output_data = {
            "id": f"{stock_data['symbol']}_{stock_data['date']}",
            "symbol": stock_data["symbol"],
            "date": stock_data["date"],
            "actual_close_price": stock_data["close_price"],
            "predicted_close_price": round(predicted_price, 2),
            "prediction_timestamp": time.time(),
        }

        print(f"Predicted: {output_data}")

        print("Sending the predicted value to predictions-topic....")

        # Publish to Kafka
        producer = create_producer()
        producer.send(OUTPUT_TOPIC, value=output_data)

        print("Sent event in predictions-topic successfully....")
        producer.flush()
        producer.close()
