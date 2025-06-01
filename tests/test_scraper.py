import pytest
from tax_bracket_ingest.scraper.fetch import fetch_irs_data

def test_fetch_irs_data():
    """
    Test the fetch_irs_data function to ensure it retrieves data from the IRS URL.
    """
    content = fetch_irs_data()
    assert isinstance(content, bytes), "Fetched content should be of type bytes."
    assert len(content) > 0, "Fetched content should not be empty."

def test_fetch_irs_data_status_code():
    """
    Test the fetch_irs_data function to ensure it retrieves data with a successful status code.
    """
    content = fetch_irs_data().decode('utf-8')  # Decode bytes to string for content checks
    assert content is not None, "Fetched content should not be None."
    
    # Check if the content is a valid HTML response
    assert "<html" in content.lower(), "Fetched content should be valid HTML."

def test_fetch_irs_data_content():
    """
    Test the fetch_irs_data function to ensure it retrieves content that contains expected keywords.
    """
    content = fetch_irs_data().decode('utf-8')  # Decode bytes to string for content checks
    assert "IRS" in content, "Fetched content should contain 'IRS'."  # Basic check for IRS content
    assert "tax rates" in content.lower(), "Fetched content should contain 'tax rates'."
    assert "brackets" in content.lower(), "Fetched content should contain 'brackets'."
    assert "filing" in content.lower(), "Fetched content should contain 'filing'."
    assert "taxpayer" in content.lower(), "Fetched content should contain 'taxpayer'."
    
    assert "Married filing jointly" in content, "Fetched content should contain 'Married Filing Jointly'."
    assert "single" in content, "Fetched content should contain 'single'."
    assert "Head of household" in content, "Fetched content should contain 'Head of Household'."
    assert "Married filing separately" in content, "Fetched content should contain 'Married Filing Separately'."

