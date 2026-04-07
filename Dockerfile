FROM python:3.10-slim

WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy environment code
COPY env/ ./env/
COPY inference.py .
COPY openenv.yaml .

# Run inference
CMD ["python", "inference.py"]
