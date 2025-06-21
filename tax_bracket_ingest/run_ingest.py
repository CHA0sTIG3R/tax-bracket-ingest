#tax_bracket_ingest/run_ingest.py
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
        print(f"Year {first_year} in historical is different from scraped — appending.")
    else:
        hist_df = prev_hist
        print(f"Year {first_year} already exists and is identical — skipping append.")
    
    # Push to backend
    push_csv_to_backend(curr_df)
    
    # update S3
    write_df_to_s3(hist_df, s3_key)
    
    print(f"Historical CSV at s3://{s3_bucket}/{s3_key} updated")

if __name__ == "__main__":
    main()