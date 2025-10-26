# Tax Bracket Ingest

> **Annual microservice** that scrapes IRS tax bracket data for the current year, sends it to a Spring backend, and archives the data in S3.

## Overview

tax\_bracket\_ingest is a standalone Python microservice designed to run once per tax year. It automatically:

1. **Fetches** the official IRS tax bracket tables for the target tax year.
2. **Parses** filing-status–specific brackets into pandas DataFrames.
3. **Normalizes** and cleans the data into a consistent CSV format.
4. **Archives** the updated CSV in an AWS S3 bucket for backup.
5. **Pushes** the new records to a downstream Spring Boot service ([*Marginal Tax Rate Calculator*](https://github.com/CHA0sTIG3R/Marginal-tax-rate-calculator)).

This ensures your backend always has the latest brackets, and you retain an immutable historical record in S3.

## Table of Contents

- [Tax Bracket Ingest](#tax-bracket-ingest)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Implementation Status](#implementation-status)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Scheduling](#scheduling)
  - [Usage](#usage)
  - [Testing](#testing)
  - [Continuous Integration](#continuous-integration)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- **Automated scraping** of IRS tax bracket HTML each year.
- **Data parsing** for all four filing statuses (Single, Married Filing Jointly, Married Filing Separately, Head of Household).
- **Normalization** to a standard CSV schema, ready for analytics or database ingestion.
- **S3 archival** to maintain a complete historical record (`history.csv` in S3).
- **Spring service integration**: HTTP POST of new bracket rows to the [Marginal-tax-rate-calculator backend](https://github.com/CHA0sTIG3R/Marginal-tax-rate-calculator).
- **Extensible design** to support additional storage backends or notification steps.
- **Comprehensive pytest suite** (unit and integration markers).
- **GitHub Actions CI** with coverage enforcement.

## Implementation Status

Below is a high-level status of the key components:

| Component                    | Status                   |
| ---------------------------- | ------------------------ |
| Fetch IRS HTML               | ✅ Implemented            |
| Parse filing-status tables   | ✅ Implemented            |
| Normalize to CSV schema      | ✅ Implemented            |
| Archive to S3                | ✅ Implemented            |
| Push to Spring backend       | ✅ Implemented            |
| Scheduled runner (cron/AWS)  | ⚙️ Manual setup required |
| Alternative storage backends | 🔲 Planned               |
| Notification hooks           | 🔲 Planned               |
| Docker containerization      | ⚙️ Optional              |

> ✅ = Complete & tested  ⚙️ = Configured but requires external setup  🔲 = Not yet implemented

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/CHA0sTIG3R/tax-bracket-ingest.git
   cd tax-bracket-ingest
   ```

2. (Recommended) Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\\Scripts\\activate   # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt        # runtime dependencies
   pip install -r requirements-dev.txt    # development & testing extras
   pip install .                          # install the package locally
   ```

## Configuration

Create a `.env` file in the project root with the following values:

```ini
# AWS S3 settings\ nS3_BUCKET=your-s3-bucket-name
S3_KEY=history.csv

# Backend API endpoint\ nBACKEND_URL=https://your-backend/api/v1/tax/upload

# AWS Credentials (if not using instance roles)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...   # optional
```

> The service uses `python-dotenv` to load these variables at runtime.

## Scheduling

Since this microservice is intended to run once per tax year (e.g., early January), you can schedule it by:

- **Cron (Linux/Mac):** Add an entry to your crontab:

  ```cron
  0 2 1 1 * cd /path/to/tax-bracket-ingest && /path/to/venv/bin/python -m tax_bracket_ingest.run_ingest >> ingest.log 2>&1
  ```

- **AWS EventBridge / CloudWatch Events:** Trigger a Lambda or ECS task on a yearly schedule.

Adjust the schedule mechanism to fit your infrastructure.

## Usage

To execute the end-to-end ingestion manually:

```bash
python -m tax_bracket_ingest.run_ingest
```

Sample output:

```txt
Fetching IRS brackets for 2025...
Found 7 rows for Single filer — appending to history.
Uploading 7 new rows to backend at https://your-backend/api/v1/tax/upload
Backing up history.csv to s3://your-s3-bucket/history.csv
```

## Testing

Run the full test suite (unit + integration):

```bash
pytest
```

- **Unit tests:** `pytest -m "not integration"`
- **Integration tests:** `pytest -m integration`

Coverage reports are generated automatically (see `coverage.xml`).

## Continuous Integration

GitHub Actions (`.github/workflows/ci.yml`) handles:

- Testing on Python 3.11 & 3.12
- Coverage minimum threshold of 90%
- Uploading reports to Codecov

```markdown
[![CI](https://github.com/CHA0sTIG3R/tax-bracket-ingest/actions/workflows/ci.yml/badge.svg)](...)
[![Codecov](https://codecov.io/gh/CHA0sTIG3R/tax-bracket-ingest/branch/main/graph/badge.svg)](...)
```

## Contributing

Feel free to open issues or PRs:

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/name`
3. Commit changes: `git commit -m "Add feature"`
4. Push and open a PR targeting `main`

Ensure tests pass and coverage remains above 90%.

## License

Currently unlicensed — a permissive license will be added in the near future.
