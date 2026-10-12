FROM python:3.12-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency definition files first for optimal layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies into project virtual environment
RUN uv sync --frozen --no-cache

# Copy application source code
COPY . .

EXPOSE 8000

# Run uvicorn server listening on all network interfaces
CMD ["uv", "run", "uvicorn", "main:app", "--host" "0.0.0.0", "--port", "8000"]