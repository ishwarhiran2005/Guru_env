FROM python:3.10-slim

WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy environment code
COPY env/ ./env/
COPY server/ ./server/
COPY inference.py .
COPY openenv.yaml .

# Environment variables (can be overridden at runtime)
ENV API_BASE_URL="https://router.huggingface.co/v1"
ENV MODEL_NAME="meta-llama/Meta-Llama-3-8B-Instruct"
# HF_TOKEN must be provided at runtime: docker run -e HF_TOKEN=your_hf_token

# Expose port for OpenEnv server
EXPOSE 7860

# Run OpenEnv server (not inference.py directly)
CMD ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
