# ─── builder stage ───────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder
WORKDIR /tax-bracket-ingest

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt setup.py ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

RUN pytest \
    --cov=tax_bracket_ingest \
    --cov-report=xml \
    --cov-report=term-missing \
    --cov-fail-under=90

# ─── final stage ────────────────────────────────────────────────────────────────
FROM python:3.11-slim
WORKDIR /tax-bracket-ingest

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only the necessary files from the builder stage
COPY --from=builder /tax-bracket-ingest/requirements.txt ./
COPY --from=builder /tax-bracket-ingest/setup.py ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=builder /tax-bracket-ingest/tax_bracket_ingest ./tax_bracket_ingest

ENTRYPOINT ["python", "-m", "tax_bracket_ingest.run_ingest"]