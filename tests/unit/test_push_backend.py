import io
import pandas as pd
import pytest

from tax_bracket_ingest.run_ingest import push_csv_to_backend

class DummyResponse:
    def __init__(self):
        self.status_code = 200
    def raise_for_status(self):
        # This method is intentionally left empty because DummyResponse always simulates a successful response (status_code 200).
        pass

def test_push_csv_to_backend_formats_and_sends(monkeypatch, sample_normalized_df):
    
    df = sample_normalized_df

    captured = {}
    def fake_post(url, headers, data, timeout):
        captured["url"]     = url
        captured["headers"] = headers
        captured["csv_text"] = (
            data.decode("utf-8") if isinstance(data, (bytes, bytearray)) else data
        )
        captured["timeout"] = timeout
        return DummyResponse()

    monkeypatch.setattr("requests.post", fake_post)

    push_csv_to_backend(df)

    assert captured["url"] == "http://fake-backend/api/tax-brackets/upload"
    assert captured["headers"]["Content-Type"] == "text/csv"
    assert captured["timeout"] == 30

    sent_df = pd.read_csv(io.StringIO(captured["csv_text"]))
    
    pd.testing.assert_frame_equal(
        sent_df.reset_index(drop=True),
        df.reset_index(drop=True),
        check_dtype=False
    )