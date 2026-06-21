# --- Stage 1: Builder ---
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
RUN pip install uv

# Copy pyproject.toml and install all backend deps into a venv
COPY pyproject.toml .
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install -e .


# --- Stage 2: Production Runner ---
FROM python:3.11-slim

WORKDIR /app

# Runtime system deps:
#   ffmpeg       → required by faster-whisper for audio decoding
#   tesseract-ocr → required by pytesseract for on-screen text OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code (includes backend/data/*.pdf)
COPY . .

# Performance & correctness settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ChromaDB will persist here inside the container
ENV CHROMA_DB_PATH="./chroma_db"

# Pre-cache the sentence-transformers embedding model (~90MB download)
# and pre-build ChromaDB from the PDFs in backend/data/
# This runs at BUILD TIME so:
#   - No API keys needed (local embeddings only)
#   - ChromaDB is baked into the image (no cold-start indexing on Render)
RUN python -m backend.scripts.index_documents

# Expose FastAPI port
EXPOSE 8000

# Start server
CMD ["uvicorn", "backend.src.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
