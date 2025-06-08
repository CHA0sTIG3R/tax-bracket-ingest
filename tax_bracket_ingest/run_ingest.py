import os
import boto3
import tempfile
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

import pandas as pd
from tax_bracket_ingest.scraper.fetch import fetch_irs_data
from tax_bracket_ingest.parser.parser import parse_irs_data, parse_irs_data_to_dataframe
from tax_bracket_ingest.parser.normalize import process_irs_dataframe, dataframe_to_csv

load_dotenv()
S3_BUCKET = os.getenv("S3_BUCKET")
S3_PREFIX = os.getenv("S3_PREFIX")

def upload_to_s3(local_path: Path, s3_key: str):
    s3 = boto3.client("s3")
    s3.upload_file(str(local_path), S3_BUCKET, s3_key)
    print(f"Uploaded {local_path.name} to s3://{S3_BUCKET}/{s3_key}")
    
def main():
    html = fetch_irs_data()
    
    raw_struct = parse_irs_data(html)
    raw_df = parse_irs_data_to_dataframe(raw_struct)
    wide_df = process_irs_dataframe(raw_df)
    
    year = wide_df['Year'][0]
    
    print(wide_df)
    
    with tempfile.TemporaryDirectory() as td:
        fn = f"brackets_{year}.csv"
        out = Path(td) / fn
        dataframe_to_csv(wide_df, str(out))
        print(out, fn)
        # upload_to_s3(out, f"{S3_PREFIX}{fn}")

if __name__ == "__main__":
    main()