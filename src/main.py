import sys
from concurrent.futures import ThreadPoolExecutor

from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from data.processed.process_csv_data import load_dataset
from producer.kafka_producer import create_producer
from producer.kafka_producer import stream_stock_data
from models.lstm_model import *
from consumer.kafka_consumer import start_consumer

import concurrent.futures


def main():
    # Load the dataset
    df_stock = load_dataset()

    # model_training_and_evaluation(df_stock)

    # Run producer & Consumer asynchronously
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(run_producer, df_stock)
        executor.submit(start_consumer)


def run_producer(df_stock):
    producer = create_producer()
    symbols = df_stock["Symbol"].unique()
    print(symbols.tolist())
    producer = create_producer()

    max_threads = min(len(symbols), 10)  # Limit max threads

    # Stream stock data to Kafka
    if symbols.size > 0:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            executor.map(
                lambda symbol: stream_stock_data(df_stock, symbol, producer), symbols
            )

    producer.close()


def model_training_and_evaluation(df_stock):
    X_train, y_train, X_val, y_val, X_test, y_test = data_preprocessing(df_stock)

    print(
        X_train.shape,
        y_train.shape,
        X_val.shape,
        y_val.shape,
        X_test.shape,
        y_test.shape,
    )

    model = create_lstm_model(X_train.shape[2])

    history = compile_and_train_lstm_model(model, X_train, y_train, X_val, y_val)

    print_metrices(history)
    plot_loss(history)
    model_evaluation(X_test, y_test)


main()
