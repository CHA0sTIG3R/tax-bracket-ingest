# tests/unit/test_parser.py
import pytest
from tax_bracket_ingest.parser.parser import (
    parse_html, 
    parse_table, 
    parse_irs_data, 
    parse_irs_data_to_dataframe
)
import pandas as pd
from bs4 import BeautifulSoup

def test_parse_html(sample_page_html):
    result = parse_html(sample_page_html)
    assert isinstance(result, dict)
    assert "Married filing jointly" in result
    assert 'table' in result["Married filing jointly"]
    assert isinstance(result["Married filing jointly"]['table'], dict)

def test_parse_table(sample_table_html):
    soup = BeautifulSoup(sample_table_html, 'html.parser')
    table = soup.find('table')
    
    result = parse_table(table)
    assert isinstance(result, dict)
    assert result.get("10%") == "$0"
    assert result.get("Tax rate") == "on taxable income from . . ."

def test_parse_irs_data(sample_page_html):
    result = parse_irs_data(sample_page_html)
    assert isinstance(result, dict)
    assert "Married filing jointly" in result
    assert "2024 tax rates for a single taxpayer" in result
    for filing_status in result:
        assert isinstance(result[filing_status]['table'], dict)
        assert "Tax rate" in result[filing_status]['table']

@pytest.fixture
def sample_irs_data():
    return {
        "Married filing jointly": {
            "table": {
                "Income Range": "$0 - $10,000",
                "Tax Rate": "10%"
            }
        },
        "Single": {
            "table": {
                "Income Range": "$0 - $5,000",
                "Tax Rate": "12%"
            }
        }
    }

def test_parse_irs_data_to_dataframe(sample_irs_data):
    df = parse_irs_data_to_dataframe(sample_irs_data)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'Header' in df.columns
    assert 'Rate' in df.columns
    assert 'Range' in df.columns
    # Parameterize expected row counts if needed
    expected_rows = 4  # Two filing statuses with two rows each
    assert len(df) == expected_rows

if __name__ == "__main__":
    pytest.main()
