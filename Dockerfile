# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /CRUDapp

# Install system dependencies
# RUN apt-get update && apt-get install -y \
#     gcc \
#     python3-dev \
#     && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /CRUDapp
# Expose port
EXPOSE 5000
# Run application
CMD python ./app.py