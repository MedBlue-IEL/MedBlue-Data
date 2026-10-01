# --- Build Stage ---
FROM python:3.11-slim AS builder

# Copy the official uv binary directly into our builder container
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable byte-compilation for faster startup, and force uv to copy packages instead of hardlinking
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# 1. Copy only configuration files first to exploit Docker layer caching
COPY pyproject.toml uv.lock ./

# 2. Pre-install dependencies strictly without the application source code
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# 3. Copy the rest of your application and sync it into the virtual environment
COPY ./src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# --- Final Production Stage ---
FROM python:3.11-slim AS runner

WORKDIR /app

# Create a secure, non-privileged user to run the server in production
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -s /bin/bash appuser

# Copy the complete pre-built virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv
COPY ./src /app/src

# Place the virtual environment's executable path first so 'uvicorn' is automatically discovered
ENV PATH="/app/.venv/bin:$PATH"

USER appuser

EXPOSE 8000

# Execute the FastAPI server natively via the venv's Uvicorn package
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]