from io import BytesIO
import os
import boto3
from dotenv import load_dotenv

import pandas as pd
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
    
def main():
    html = fetch_irs_data()
    
    raw_struct = parse_irs_data(html.decode('utf-8'))
    raw_df = parse_irs_data_to_dataframe(raw_struct)
    curr_df = process_irs_dataframe(raw_df)
    
    s3_bucket, s3_key = load_env_vars()
    
    prev_hist = read_csv_from_s3(s3_key)
    
    hist_df = pd.concat([curr_df, prev_hist], ignore_index=True)
    
    #TODO: check for duplicated years in case and tax rates in case of running scraper too early or IRS not being updated on time
    
    write_df_to_s3(hist_df, s3_key)
    
    print(f"Historical CSV at s3://{s3_bucket}/{s3_key} updated")

if __name__ == "__main__":
    main()