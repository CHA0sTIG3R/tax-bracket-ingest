import pytest
from tax_bracket_ingest.scraper.fetch import fetch_irs_data

def test_fetch_irs_data():
    """
    Test the fetch_irs_data function to ensure it retrieves data from the IRS URL.
    """
    content = fetch_irs_data()
    assert isinstance(content, bytes), "Fetched content should be of type bytes."
    assert len(content) > 0, "Fetched content should not be empty."
    assert "IRS" in content, "Fetched content should contain 'IRS'."  # Basic check for IRS content

def test_fetch_irs_data_status_code():
    """
    Test the fetch_irs_data function to ensure it retrieves data with a successful status code.
    """
    content = fetch_irs_data()
    assert content is not None, "Fetched content should not be None."
    
    # Check if the content is a valid HTML response
    assert "<html" in content.lower(), "Fetched content should be valid HTML."

def test_fetch_irs_data_content():
    """
    Test the fetch_irs_data function to ensure it retrieves content that contains expected keywords.
    """
    content = fetch_irs_data()
    assert "tax rates" in content.lower(), "Fetched content should contain 'tax rates'."
    assert "brackets" in content.lower(), "Fetched content should contain 'brackets'."
    assert "filing" in content.lower(), "Fetched content should contain 'filing'."
    
    assert "Married Filing Jointly" in content, "Fetched content should contain 'Married Filing Jointly'."
    assert "Single Filer" in content, "Fetched content should contain 'Single Filer'."
    assert "Head of Household" in content, "Fetched content should contain 'Head of Household'."
    assert "Married Filing Separately" in content, "Fetched content should contain 'Married Filing Separately'."

