#!/bin/bash

# Function to check if Kafka is ready
check_kafka() {
    docker exec broker kafka-topics.sh --list --bootstrap-server broker:29092 2>/dev/null
    return $?
}

echo "Waiting for Kafka to be ready..."

# Wait for up to 60 seconds for Kafka to be ready
COUNTER=0
until check_kafka || [ $COUNTER -eq 60 ]; do
    echo "Waiting for Kafka to be ready... ($COUNTER seconds)"
    sleep 1
    ((COUNTER++))
done

if [ $COUNTER -eq 60 ]; then
    echo "Error: Timed out waiting for Kafka to be ready"
    echo "Checking Kafka logs:"
    docker-compose logs broker
    exit 1
fi

echo "Kafka is ready! Creating topics..."

# Create topics
docker exec broker kafka-topics.sh \
    --create \
    --if-not-exists \
    --bootstrap-server broker:29092 \
    --replication-factor 1 \
    --partitions 1 \
    --topic input-data

docker exec broker kafka-topics.sh \
    --create \
    --if-not-exists \
    --bootstrap-server broker:29092 \
    --replication-factor 1 \
    --partitions 1 \
    --topic predictions

# List topics
echo "Created topics:"
docker exec broker kafka-topics.sh --list --bootstrap-server broker:29092 