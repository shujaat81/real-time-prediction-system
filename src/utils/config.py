import os

# Kafka Configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:29092')
INPUT_TOPIC = 'input-data'
PREDICTION_TOPIC = 'predictions'

# Model Configuration
MODEL_PATH = '/app/models/model.h5'

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO') 