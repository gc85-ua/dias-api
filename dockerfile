# Builder stage
FROM python:3.12-slim AS builder

# Install uv from the official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
# Set the working directory where the application code will be copied
WORKDIR /project
# Copy dependencies files
COPY pyproject.toml uv.lock ./
# Install dependencies into a virtual environment
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application code
COPY . .

# Install the application itself into the existing venv
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.12-slim AS runtime

# Security: Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /project -s /sbin/nologin appuser
# Set runtime working directory
WORKDIR /project

# Copy the virtual environment and the app code from the builder
# We only need the .venv and the actual source code, not the build tools
# Owership is set to root:appuser so that the appuser group can be set to read and execute the files
COPY --from=builder --chown=root:appuser /project/.venv /project/.venv
COPY --from=builder --chown=root:appuser /project/app /project/app
COPY --from=builder --chown=root:appuser /project/data /project/data

# Security: Allow appuser to read and execute source code
RUN chmod -R 750 /project/.venv
RUN chmod -R 750 /project/app
RUN chmod -R 750 /project/data

# Add the virtual environment to the PATH so `python` and `uvicorn` resolve correctly
ENV PATH="/project/.venv/bin:$PATH"

# Add default cache environment variables
ENV CACHE_DB_HOST="localhost"
ENV CACHE_DB_PORT="6379"
ENV CACHE_DB="0"

# Add default OTel environment variables for OTLP exporter
ENV OTEL_SERVICE_NAME="laborables-api"
ENV OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
ENV OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"

# Expose the port FastAPI will run on
EXPOSE 8000

# Switch to non-root user
USER appuser
# Use OTel instrumentation to run the app
CMD ["opentelemetry-instrument", "uvicorn", "app.main:app", "--port", "8000", "--host", "0.0.0.0"]