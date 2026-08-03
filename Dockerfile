# Build stage
FROM python:3.10-slim as builder

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY privacy_filter/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Download primary spaCy model
RUN python -m spacy download en_core_web_sm

# Final runtime stage
FROM python:3.10-slim as runner

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy codebase
COPY privacy_filter/ /app/privacy_filter/

# Set Python Path to resolve modules
ENV PYTHONPATH=/app

EXPOSE 8050

CMD ["python", "-m", "privacy_filter.web.server"]
