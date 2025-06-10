from pathlib import Path
from moto import mock_aws
import pytest
import pandas as pd
import boto3

TEST_DATA = Path(__file__).parent / "data"

@pytest.fixture(scope="session")
def test_data_dir():
    """Path to tests/data"""
    return TEST_DATA

@pytest.fixture
def sample_page_html(test_data_dir):
    return (test_data_dir / "sample_page.html").read_text(encoding='utf-8')
    
@pytest.fixture
def sample_table_html(sample_page_html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(sample_page_html, 'html.parser')
    table = soup.find('table')
    return str(table) if table else None

@pytest.fixture
def sample_raw_csv(test_data_dir):
    return pd.read_csv(test_data_dir / "sample_raw.csv")

@pytest.fixture
def sample_normalized_df(test_data_dir):
    return pd.read_csv(test_data_dir / "sample_normalized.csv")

@pytest.fixture
def moto_s3_client():
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        yield s3
        # Cleanup after test
        for bucket in s3.list_buckets()["Buckets"]:
            s3.delete_bucket(Bucket=bucket["Name"])

@pytest.fixture
def s3_bucket(moto_s3_client):
    with mock_aws():
        bucket_name = "test-bucket"
        moto_s3_client.create_bucket(Bucket=bucket_name)
        yield bucket_name
        # Cleanup after test
        moto_s3_client.delete_bucket(Bucket=bucket_name)

@pytest.fixture(autouse=True)
def env_vars(monkeypatch, s3_bucket):
    monkeypatch.setenv("S3_BUCKET", s3_bucket)
    monkeypatch.setenv("S3_KEY", "history.csv")