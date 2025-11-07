FROM python:3.11-slim

# Install Stockfish chess engine
RUN apt-get update && \
    apt-get install -y --no-install-recommends stockfish && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .

# Environment variables
ENV STOCKFISH_PATH=/usr/games/stockfish
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run the server
CMD ["python", "server.py"]
```
