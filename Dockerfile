# ─── builder stage ───────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder
WORKDIR /app 

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt setup.py ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Build the package
RUN pip install --no-cache-dir build && python -m build --wheel -o /dist

# ─── final stage ────────────────────────────────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

RUN useradd -m -u 10001 appuser

# Create log directory
RUN mkdir -p logs && chown appuser:appuser logs

# Copy only the necessary files from the builder stage
COPY --from=builder /dist/*.whl  /tmp/
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl \
    && rm -rf /usr/local/lib/python3.11/site-packages/build \
    && rm -rf /usr/local/lib/python3.11/site-packages/pip \
    && rm -rf /usr/local/lib/python3.11/site-packages/setuptools \
    && rm -rf /usr/local/lib/python3.11/site-packages/wheel

COPY tax_bracket_ingest ./tax_bracket_ingest

USER appuser

ENTRYPOINT ["python", "-m", "tax_bracket_ingest.run_ingest"]