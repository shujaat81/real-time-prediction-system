FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and models
COPY src/ ./src/
COPY models/ ./models/

CMD ["python", "-m", "src.consumer.data_consumer"] 