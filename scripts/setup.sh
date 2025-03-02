#!/bin/bash

# Create project directories
mkdir -p src/{producer,consumer,utils,monitoring}
mkdir -p data/{raw,processed}
mkdir -p models
mkdir -p docker
mkdir -p tests
mkdir -p notebooks

# Create empty __init__.py files
touch src/__init__.py
touch src/producer/__init__.py
touch src/consumer/__init__.py
touch src/utils/__init__.py
touch src/monitoring/__init__.py

# Create .gitkeep files for empty directories
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch models/.gitkeep

# Start Kafka in detached mode
docker-compose down -v
docker-compose up -d

echo "Waiting for Kafka broker to start..."
sleep 10

# Check broker is running
if [ $(docker ps -q -f name=broker) ]; then
    echo "Broker container is running"
else
    echo "Broker container is not running"
    docker-compose logs broker
    exit 1
fi

# Wait for Kafka to be fully ready
MAX_ATTEMPTS=30
ATTEMPT=0
READY=false

while [ $ATTEMPT -lt $MAX_ATTEMPTS ] && [ "$READY" = false ]; do
    ATTEMPT=$((ATTEMPT+1))
    echo "Checking if Kafka is ready... Attempt $ATTEMPT of $MAX_ATTEMPTS"
    
    if docker exec broker kafka-topics.sh --list --bootstrap-server broker:29092 &>/dev/null; then
        READY=true
        echo "Kafka is ready!"
    else
        echo "Kafka is not ready yet, waiting..."
        sleep 5
    fi
done

if [ "$READY" = false ]; then
    echo "Kafka did not become ready in time. Check logs:"
    docker-compose logs broker
    exit 1
fi

# Create topics
echo "Creating Kafka topics..."
docker exec broker kafka-topics.sh --create --if-not-exists --bootstrap-server broker:29092 --replication-factor 1 --partitions 1 --topic input-data
docker exec broker kafka-topics.sh --create --if-not-exists --bootstrap-server broker:29092 --replication-factor 1 --partitions 1 --topic predictions

# List topics
echo "Created topics:"
docker exec broker kafka-topics.sh --list --bootstrap-server broker:29092

echo "Kafka setup complete!" 