# tax_bracket_ingest/run_ingest.py
from tax_bracket_ingest.logging_config import setup_logging
setup_logging()

import logging
logger = logging.getLogger(__name__)

import os
from io import BytesIO

import boto3
import pandas as pd
import requests

from tax_bracket_ingest.scraper.fetch import fetch_irs_data
from tax_bracket_ingest.parser.parser import parse_irs_data, parse_irs_data_to_dataframe
from tax_bracket_ingest.parser.normalize import process_irs_dataframe

TRUTHY_ENV_VALUES = {"1", "true", "t", "yes", "y", "on"}
DRY_RUN = os.getenv("DRY_RUN", "").strip().lower() in TRUTHY_ENV_VALUES
print(f'DRY_RUN is set to {DRY_RUN}')

def load_env_vars():
    s3_bucket = os.getenv("S3_BUCKET")
    s3_key = os.getenv("S3_KEY")
    print(f's3_bucket: {s3_bucket}, s3_key: {s3_key}')
    
    return s3_bucket, s3_key
    
def read_csv_from_s3(key: str) -> pd.DataFrame:
    s3 = boto3.client("s3")
    print(f'bucket: {load_env_vars()[0]}, key: {key}')
    resp = s3.get_object(Bucket=load_env_vars()[0], Key=key)
    return pd.read_csv(BytesIO(resp["Body"].read()))

def write_df_to_s3(df: pd.DataFrame, key: str):
    if DRY_RUN:
        logger.info(
            "dry_run_skip_write_s3",
            extra={
                "rows": len(df),
                "s3_key": key,
                "action": "Skipped writing historical CSV to S3 in dry-run mode",
            },
        )
        return
    s3 = boto3.client("s3")
    buf = BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    s3.put_object(Bucket=load_env_vars()[0], Key=key, Body=buf.getvalue())
    
def push_csv_to_backend(df: pd.DataFrame):
    if DRY_RUN:
        logger.info(
            "dry_run_skip_backend_push",
            extra={
                "rows": len(df),
                "action": "Skipped pushing current tax data to backend in dry-run mode",
            },
        )
        return "dry_run_skipped"
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    url = os.getenv("BACKEND_URL") + "/api/v1/tax/upload"
    headers = {
        "Content-Type": "text/csv", 
        "X-API-KEY": os.getenv("INGEST_API_KEY")
    }
    resp = requests.post(
        url,
        headers=headers,
        data=csv_bytes,
        timeout=30
    )
    resp.raise_for_status()
    return resp.content.decode('utf-8')
    
    
def main():
    if DRY_RUN:
        logger.info(
            "dry_run_mode",
            extra={"action": "Running ingest process in dry-run mode"},
        )
    html = fetch_irs_data()
    
    raw_struct = parse_irs_data(html.decode('utf-8'))
    raw_df = parse_irs_data_to_dataframe(raw_struct)
    curr_df = process_irs_dataframe(raw_df)
    
    s3_bucket, s3_key = load_env_vars()
    
    if DRY_RUN:
        hist_df = curr_df
        logger.info(
            "dry_run_skip_history_fetch",
            extra={
                "rows": len(curr_df),
                "action": "Skipped fetching historical CSV from S3 in dry-run mode",
            },
        )
    else:
        prev_hist = read_csv_from_s3(s3_key)
        
        first_year = prev_hist.iloc[0]["Year"]
        recent_year_rows = prev_hist[prev_hist["Year"] == first_year]

        # Compare and append only if new
        if not curr_df.equals(recent_year_rows):
            hist_df = pd.concat([curr_df, prev_hist], ignore_index=True)
            logger.info("append_new_data", extra={
                "year": first_year,
                "rows_added": len(curr_df),
                "action": "Appending new data to historical CSV"
            })
        else:
            hist_df = prev_hist
            logger.info("skipping_append", extra={
                "year": first_year,
                "rows": len(curr_df),
                "action": "No new data to append, skipping"
            })
    
    # Push to backend
    resp = push_csv_to_backend(curr_df)
    if not DRY_RUN:
        logger.info("pushed_to_backend",  extra={
            "rows": len(curr_df),
            "response": resp,
            "action": "Pushed current tax data to backend"
        })
    
    # update S3
    write_df_to_s3(hist_df, s3_key)
    if not DRY_RUN:
        logger.info("updated_s3",  extra={
            "s3_bucket": s3_bucket,
            "s3_key": s3_key,
            "rows": len(hist_df),
            "action": "Updated historical CSV in S3"
        })
    
    logger.info("ingest_complete", extra={"action": "Ingest process completed successfully"})

if __name__ == "__main__":
    logger.info("starting_ingest",  extra={"action": "Starting ingest process"})
    try:
        main()
    except Exception as e:
        logger.error("ingest_error", error=str(e), extra={"action": "Error during ingest process"})
        raise
    finally:
        logger.info("ingest_finished", extra={"action": "Ingest process finished"})
        print("Ingest process completed. Check logs for details.")
