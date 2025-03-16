import json
import time
import random
from kafka import KafkaProducer

# Kafka Configuration
KAFKA_BROKER = "localhost:9092"
TOPIC_NAME = "stock-input-data-topic"


# Initialize Kafka Producer
def create_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        acks=1,  # Ensure message delivery
    )


# Function to stream stock data
def stream_stock_data(df_stock, symbol, producer):
    stock_data = df_stock[df_stock["Symbol"] == symbol]

    if stock_data.empty:
        print(f"No data found for {symbol}")
        return

    print(stock_data.head(5))

    for _, row in stock_data.iterrows():
        message = {
            "id": f"{row['Symbol']}_{row['Date'].strftime('%Y-%m-%d')}",
            "symbol": row["Symbol"],
            "date": row["Date"].strftime("%Y-%m-%d"),
            "open_price": row["Open"],
            "high_price": row["High"],
            "low_price": row["Low"],
            "close_price": row["Close"],
            "volume": row["Volume"],
            "timestamp": time.time(),
        }

        print(f"[{symbol}] Produced: {message}")

        """Produces stock events for a given symbol"""
        future = producer.send(TOPIC_NAME, value=message)
        producer.flush()  # Ensure message is sent immediately

        try:
            record_metadata = future.get(timeout=10)
            print(
                f"Message sent to {record_metadata.topic} partition {record_metadata.partition}"
            )
        except Exception as e:
            print(f"Error sending message: {e}")

        # Simulating real-time streaming
        time.sleep(random.uniform(0.2, 1))
