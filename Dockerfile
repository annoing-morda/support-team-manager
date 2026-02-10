# Multi-stage build for optimal image size
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir build

# Copy project files
COPY pyproject.toml .
COPY bot/ bot/

# Build wheel
RUN python -m build --wheel

# Runtime stage
FROM python:3.11-slim as runtime

# Create non-root user
RUN useradd --create-home appuser

WORKDIR /home/appuser/app

# Copy wheel from builder
COPY --from=builder /app/dist/*.whl .

# Install the package
RUN pip install --no-cache-dir *.whl && rm *.whl

# Copy migrations
COPY migrations/ migrations/
COPY alembic.ini .

# Switch to non-root user
USER appuser

# Run the bot
CMD ["python", "-m", "bot"]
