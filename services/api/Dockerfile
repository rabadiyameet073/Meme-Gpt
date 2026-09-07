# This Dockerfile builds the actual backend from the backend/ directory.
# It exists here for docker-compose compatibility.

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      tesseract-ocr \
      libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from the real backend
COPY ../../backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download ML models during build
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" || true
RUN python -c "from transformers import pipeline; pipeline('text-classification', model='j-hartmann/emotion-english-distilroberta-base')" || true

# Copy the actual backend code
COPY ../../backend/ .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
