# Docker Deployment Guide

This guide explains how to run the Manga Colorizer backend using Docker.

## Prerequisites

- Docker (20.10+)
- Docker Compose (2.0+)
- For GPU support: [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

## Quick Start

### 1. Download Model Weights

**⚠️ IMPORTANT:** Before running the Docker container, you must download the colorizer model weights.

1. Download `generator.zip` from [Google Drive](https://drive.google.com/file/d/1qmxUEKADkEM4iYLp1fpPLLKnfZ6tcF-t/view?usp=sharing)
2. Place it in `Backend/networks/generator.zip`

The other required models are already included in the repository:

- ✅ `Backend/networks/RealESRGAN_x4plus_anime_6B.pt` (upscaler)
- ✅ `Backend/denoising/models/net_rgb.pth` (denoiser)

### 2. Run with Docker Compose

**For CPU:**

```bash
docker-compose up -d
```

**For GPU:**

1. Uncomment the GPU configuration in `docker-compose.yml`:

   - Uncomment `runtime: nvidia`
   - Uncomment the `deploy` section
   - Change `DEVICE=cpu` to `DEVICE=cuda`
   - Or use the alternative GPU configuration at the bottom of the file

2. Run:

```bash
docker-compose up -d
```

### 3. Verify It's Running

```bash
# Check logs
docker-compose logs -f

# Test the endpoint
curl http://localhost:5000
# Should return: "Manga Colorizer is Up and Running!"
```

## Building Locally

If you want to build the Docker image locally instead of using GitHub Actions:

### CPU Version

```bash
cd Backend
docker build --build-arg BUILD_TYPE=cpu -t manga-colorizer:cpu .
```

### GPU Version

```bash
cd Backend
docker build --build-arg BUILD_TYPE=gpu -t manga-colorizer:gpu .
```

### Run Locally Built Image

```bash
# CPU
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/Backend/networks:/app/networks:ro \
  -v $(pwd)/Backend/denoising/models:/app/denoising/models:ro \
  -v manga-cache:/app/manga \
  -e DEVICE=cpu \
  -e SSL_ENABLED=false \
  manga-colorizer:cpu

# GPU (requires nvidia-docker)
docker run -d \
  --runtime=nvidia \
  --gpus all \
  -p 5000:5000 \
  -v $(pwd)/Backend/networks:/app/networks:ro \
  -v $(pwd)/Backend/denoising/models:/app/denoising/models:ro \
  -v manga-cache:/app/manga \
  -e DEVICE=cuda \
  -e SSL_ENABLED=false \
  manga-colorizer:gpu
```

## Environment Variables

| Variable         | Default                                  | Description                                    |
| ---------------- | ---------------------------------------- | ---------------------------------------------- |
| `DEVICE`         | `cpu` or `cuda`                          | Compute device to use                          |
| `COLORIZER_PATH` | `networks/generator.zip`                 | Path to colorizer model weights                |
| `UPSCALER_PATH`  | `networks/RealESRGAN_x4plus_anime_6B.pt` | Path to upscaler model                         |
| `EXTRACTOR_PATH` | `networks/extractor.pth`                 | Path to extractor model (not currently used)   |
| `SSL_ENABLED`    | `false`                                  | Enable HTTPS (requires certificates in `ssl/`) |

You can override these in `docker-compose.yml` or pass them via `-e` flag with `docker run`.

## Volume Mounts

The following directories are mounted as volumes:

- **`./Backend/networks:/app/networks:ro`** - Model weights (read-only, must include `generator.zip`)
- **`./Backend/denoising/models:/app/denoising/models:ro`** - Denoising models (read-only)
- **`manga-cache:/app/manga`** - Persistent cache for processed images
- **`./Backend/ssl:/app/ssl:ro`** (optional) - SSL certificates if `SSL_ENABLED=true`
- **`./Backend/input:/app/input`** (optional) - Input images for batch processing
- **`./Backend/output:/app/output`** (optional) - Output images from batch processing

## GitHub Actions CI/CD

The repository includes a GitHub Actions workflow that automatically builds and pushes Docker images to GitHub Container Registry (GHCR) when you push to the `main` or `master` branch.

### Automatic Builds

The workflow builds two image variants:

- **CPU**: `ghcr.io/<username>/<repo>:cpu`, `ghcr.io/<username>/<repo>:latest-cpu`
- **GPU**: `ghcr.io/<username>/<repo>:gpu`, `ghcr.io/<username>/<repo>:latest-gpu`, `ghcr.io/<username>/<repo>:latest`

### Using GitHub Actions Images

After the workflow runs successfully:

1. Go to your repository → Packages
2. Find the `manga-colorizer` package
3. Copy the image URL
4. Update `docker-compose.yml` with the correct image name
5. Pull and run:

```bash
docker-compose pull
docker-compose up -d
```

### Making Images Public

By default, GitHub Container Registry images are private. To make them public:

1. Go to your repository → Packages → manga-colorizer
2. Click "Package settings"
3. Scroll to "Danger Zone" → Change visibility → Public

## Expected Image Sizes

- **CPU Image**: ~1.5-2 GB (using `python:3.10-slim`)
- **GPU Image**: ~3-4 GB (using `nvidia/cuda:11.8.0-cudnn8-runtime`)

Sizes are optimized using:

- Multi-stage builds
- Minimal base images (slim/runtime, not full/devel)
- CPU-only PyTorch for CPU builds
- `--no-cache-dir` for pip installations

## Troubleshooting

### "generator.zip not found"

**Problem**: Container fails to start with error about missing colorizer weights.

**Solution**: Download `generator.zip` and place it in `Backend/networks/` before starting the container.

### GPU Not Detected

**Problem**: Container runs but uses CPU instead of GPU.

**Solution**:

1. Verify NVIDIA Container Toolkit is installed: `docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi`
2. Ensure `runtime: nvidia` is uncommented in `docker-compose.yml`
3. Set `DEVICE=cuda` environment variable
4. Check container logs for CUDA errors

### Out of Memory

**Problem**: Container crashes with CUDA out of memory errors.

**Solution**:

1. Process smaller images
2. Reduce upscale factor (2 instead of 4)
3. Disable upscaling with `--no-upscale` flag
4. Add memory limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 8G
```

### Port Already in Use

**Problem**: Cannot bind to port 5000.

**Solution**: Change port mapping in `docker-compose.yml`:

```yaml
ports:
  - "8080:5000" # Use 8080 on host instead
```

## Health Check

The container includes a health check that runs every 30 seconds:

```bash
# Check health status
docker-compose ps

# View health check logs
docker inspect --format='{{.State.Health}}' manga-colorizer-backend
```

## Stopping and Cleaning Up

```bash
# Stop the container
docker-compose down

# Stop and remove volumes (deletes cache)
docker-compose down -v

# Remove images
docker rmi ghcr.io/<username>/<repo>:latest
```

## Advanced Usage

### Custom Configuration

Create a `docker-compose.override.yml` for local customizations:

```yaml
version: "3.8"

services:
  manga-colorizer:
    environment:
      - DEVICE=cuda
      - SSL_ENABLED=true
    volumes:
      - ./custom-ssl:/app/ssl:ro
    ports:
      - "8080:5000"
```

### Development Mode

For development, mount the entire backend directory:

```yaml
volumes:
  - ./Backend:/app
command: python app-stream.py --device cpu --no-ssl
```

### Batch Processing

To run batch processing instead of the server:

```bash
docker run --rm \
  -v $(pwd)/Backend/networks:/app/networks:ro \
  -v $(pwd)/Backend/input:/app/input \
  -v $(pwd)/Backend/output:/app/output \
  ghcr.io/<username>/<repo>:cpu \
  python inference.py --device cpu
```

## Support

For issues related to:

- Docker setup: Check this document and Docker logs
- Model downloads: See the main README.md
- Application errors: Check application logs with `docker-compose logs -f`
