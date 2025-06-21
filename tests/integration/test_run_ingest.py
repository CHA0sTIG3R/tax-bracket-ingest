# tests/integration/test_run_ingest.py
import io
import pandas as pd
import pytest
import requests
from tax_bracket_ingest.run_ingest import main as run_ingest_main

@pytest.mark.integration
def test_run_ingest_end_to_end(
    moto_s3_client,
    sample_page_html, sample_normalized_csv_bytes,
    sample_normalized_df, capsys, monkeypatch,
    dummy_response
):
    
    bucket_name = "test-bucket"
    
    moto_s3_client.create_bucket(Bucket=bucket_name)
    
    moto_s3_client.put_object(
        Bucket=bucket_name,
        Key="history.csv",
        Body=sample_normalized_csv_bytes
    )

    
    import tax_bracket_ingest.scraper.fetch as fetch_mod
    fetch_mod.fetch_irs_data = lambda: sample_page_html
    
    captured = {}
    def fake_post(url, headers, data, timeout):
        captured["url"]      = url
        captured["headers"]  = headers
        captured["body_csv"] = data.decode("utf-8")
        return dummy_response
    
    monkeypatch.setattr(requests, "post", fake_post)
    
    run_ingest_main()
    
    resp = moto_s3_client.get_object(Bucket=bucket_name, Key="history.csv")
    updated_csv = resp["Body"].read().decode("utf-8")
    updated_df = pd.read_csv(io.StringIO(updated_csv))
    
    pushed_df = pd.read_csv(io.StringIO(captured["body_csv"]))
    
    from tax_bracket_ingest.parser.parser import (
        parse_irs_data_to_dataframe,
        parse_irs_data,
    )
    from tax_bracket_ingest.parser.normalize import process_irs_dataframe

    raw_struct = parse_irs_data(sample_page_html.decode("utf-8"))
    new_df = process_irs_dataframe(parse_irs_data_to_dataframe(raw_struct))
    old_df = sample_normalized_df

    # 6. Validate
    assert captured["url"].endswith("/api/v1/tax/upload")
    assert captured["headers"]["Content-Type"] == "text/csv"
    assert len(updated_df) == len(new_df) + len(old_df)
    pd.testing.assert_frame_equal(
        updated_df.iloc[:len(new_df)].reset_index(drop=True),
        new_df.reset_index(drop=True),
        check_dtype=False
    )
    pd.testing.assert_frame_equal(
        updated_df.iloc[len(new_df):].reset_index(drop=True),
        old_df.reset_index(drop=True),
        check_dtype=False
    )
    
    pd.testing.assert_frame_equal(
        pushed_df.reset_index(drop=True),
        new_df.reset_index(drop=True),
        check_dtype=False
    )
