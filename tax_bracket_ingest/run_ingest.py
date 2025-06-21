# tax_bracket_ingest/run_ingest.py
from tax_bracket_ingest.logging_config import setup_logging
setup_logging()

import logging
logger = logging.getLogger(__name__)

from io import BytesIO
import os
import boto3
from dotenv import load_dotenv

import pandas as pd
import requests
from tax_bracket_ingest.scraper.fetch import fetch_irs_data
from tax_bracket_ingest.parser.parser import parse_irs_data, parse_irs_data_to_dataframe
from tax_bracket_ingest.parser.normalize import process_irs_dataframe

def load_env_vars():
    load_dotenv()
    
    s3_bucket = os.getenv("S3_BUCKET")
    s3_key = os.getenv("S3_KEY")
    
    return s3_bucket, s3_key
    
def read_csv_from_s3(key: str) -> pd.DataFrame:
    s3 = boto3.client("s3")
    resp = s3.get_object(Bucket=load_env_vars()[0], Key=key)
    return pd.read_csv(BytesIO(resp["Body"].read()))

def write_df_to_s3(df: pd.DataFrame, key: str):
    s3 = boto3.client("s3")
    buf = BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    s3.put_object(Bucket=load_env_vars()[0], Key=key, Body=buf.getvalue())
    
def push_csv_to_backend(df: pd.DataFrame):
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
    
    
def main():
    html = fetch_irs_data()
    
    raw_struct = parse_irs_data(html.decode('utf-8'))
    raw_df = parse_irs_data_to_dataframe(raw_struct)
    curr_df = process_irs_dataframe(raw_df)
    
    s3_bucket, s3_key = load_env_vars()
    
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
    push_csv_to_backend(curr_df)
    logger.info("pushed_to_backend",  extra={
        "rows": len(curr_df),
        "action": "Pushed current tax data to backend"
    })
    
    # update S3
    write_df_to_s3(hist_df, s3_key)
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