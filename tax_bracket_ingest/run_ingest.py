from io import BytesIO
import os
import boto3
from dotenv import load_dotenv

import pandas as pd
from tax_bracket_ingest.scraper.fetch import fetch_irs_data
from tax_bracket_ingest.parser.parser import parse_irs_data, parse_irs_data_to_dataframe
from tax_bracket_ingest.parser.normalize import process_irs_dataframe

load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_PREFIX = os.getenv("S3_PREFIX")
S3_KEY = os.getenv("S3_KEY")
    
def read_csv_from_s3(key: str) -> pd.DataFrame:
    s3 = boto3.client("s3")
    resp = s3.get_object(Bucket=S3_BUCKET, Key=key)
    return pd.read_csv(BytesIO(resp["Body"].read()))

def write_df_to_s3(df: pd.DataFrame, key: str):
    s3 = boto3.client("s3")
    buf = BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=buf.getvalue())
    
def main():
    html = fetch_irs_data()
    
    raw_struct = parse_irs_data(html)
    raw_df = parse_irs_data_to_dataframe(raw_struct)
    curr_df = process_irs_dataframe(raw_df)
    
    prev_hist = read_csv_from_s3(S3_KEY)
    
    hist_df = pd.concat([curr_df, prev_hist], ignore_index=True)
    
    write_df_to_s3(hist_df, S3_KEY)
    
    print(f"Historical CSV at s3://{S3_BUCKET}/{S3_KEY} updated")

if __name__ == "__main__":
    main()