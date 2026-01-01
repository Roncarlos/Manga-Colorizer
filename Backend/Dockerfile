# Multi-stage Dockerfile for Manga-Colorizer Backend
# Supports both CPU and GPU builds with minimal image sizes
# Build args: BUILD_TYPE=cpu or BUILD_TYPE=gpu

ARG BUILD_TYPE=cpu

# ============================================================================
# Stage 1: CPU Builder
# ============================================================================
FROM python:3.10-slim AS builder-cpu

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies with CPU-only PyTorch
RUN pip install --no-cache-dir --user \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# Stage 2: GPU Builder
# ============================================================================
FROM nvidia/cuda:13.0.2-cudnn-devel-ubuntu24.04 AS builder-gpu

WORKDIR /build

# Install Python 3.12 (default in Ubuntu 24.04) and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-dev \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic links for python
RUN ln -sf /usr/bin/python3.12 /usr/bin/python && \
    ln -sf /usr/bin/python3.12 /usr/bin/python3

# Upgrade pip
RUN python -m pip install --no-cache-dir --upgrade pip

# Copy requirements
COPY requirements.txt .

# Install Python dependencies with CUDA-enabled PyTorch
# Using cu121 wheels which are forward compatible with CUDA 13.x
RUN pip install --no-cache-dir --user \
    torch torchvision --index-url https://download.pytorch.org/whl/cu121 && \
    pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# Stage 3: CPU Runtime
# ============================================================================
FROM python:3.10-slim AS runtime-cpu

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder-cpu /root/.local /root/.local

# Add local bin to PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p networks denoising/models utils input output manga ssl

# Environment variables with defaults
ENV DEVICE=cpu \
    COLORIZER_PATH=networks/generator.zip \
    UPSCALER_PATH=networks/RealESRGAN_x4plus_anime_6B.pt \
    EXTRACTOR_PATH=networks/extractor.pth \
    SSL_ENABLED=false \
    PYTHONUNBUFFERED=1

# Expose Flask port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000')" || exit 1

# Run the application
CMD ["python", "app-stream.py"]

# ============================================================================
# Stage 4: GPU Runtime
# ============================================================================
FROM nvidia/cuda:13.0.2-cudnn-runtime-ubuntu24.04 AS runtime-gpu

WORKDIR /app

# Install Python 3.12 (default in Ubuntu 24.04) and runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3-pip \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic links for python
RUN ln -sf /usr/bin/python3.12 /usr/bin/python && \
    ln -sf /usr/bin/python3.12 /usr/bin/python3

# Copy Python packages from builder
COPY --from=builder-gpu /root/.local /root/.local

# Add local bin to PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p networks denoising/models utils input output manga ssl

# Environment variables with defaults
ENV DEVICE=cuda \
    COLORIZER_PATH=networks/generator.zip \
    UPSCALER_PATH=networks/RealESRGAN_x4plus_anime_6B.pt \
    EXTRACTOR_PATH=networks/extractor.pth \
    SSL_ENABLED=false \
    PYTHONUNBUFFERED=1

# Expose Flask port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000')" || exit 1

# Run the application
CMD ["python", "app-stream.py"]

# ============================================================================
# Final stage selection based on BUILD_TYPE
# ============================================================================
FROM runtime-${BUILD_TYPE} AS final
