# --- Stage 1: Builder ---
# We use a standard Python image to build the dependencies.
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Use 'uv' for extremely fast dependency installation
RUN pip install uv

# Copy only requirements first to cache the dependency layer
COPY azure_functions/requirements.txt .

# Create a virtual environment and install dependencies into it
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install -r requirements.txt


# --- Stage 2: Production Runner ---
# Use a minimal slim image for the final container to reduce attack surface and size.
FROM python:3.11-slim

WORKDIR /app

# Install runtime system dependencies (e.g., ffmpeg is often needed by yt-dlp)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Set production environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Start the FastAPI server using Uvicorn
CMD ["uvicorn", "backend.src.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
