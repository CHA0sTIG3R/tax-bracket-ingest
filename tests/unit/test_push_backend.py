# tests/unit/test_push_backend.py
import io
import pandas as pd
import pytest

from tax_bracket_ingest.run_ingest import push_csv_to_backend

def test_push_csv_to_backend_formats_and_sends(monkeypatch, sample_normalized_df, dummy_response):
    
    df = sample_normalized_df

    captured = {}
    def fake_post(url, headers, data, timeout):
        captured["url"]     = url
        captured["headers"] = headers
        captured["csv_text"] = (
            data.decode("utf-8") if isinstance(data, (bytes, bytearray)) else data
        )
        captured["timeout"] = timeout
        return dummy_response

    monkeypatch.setattr("requests.post", fake_post)

    response = push_csv_to_backend(df)
    assert response == "dummy content"
    assert captured["url"] == "http://fake-backend/api/v1/tax/upload"
    assert captured["headers"]["Content-Type"] == "text/csv"
    assert captured["timeout"] == 30

    sent_df = pd.read_csv(io.StringIO(captured["csv_text"]))
    
    pd.testing.assert_frame_equal(
        sent_df.reset_index(drop=True),
        df.reset_index(drop=True),
        check_dtype=False
    )