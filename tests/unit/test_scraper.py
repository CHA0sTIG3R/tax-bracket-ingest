import pytest
from tax_bracket_ingest.scraper.fetch import fetch_irs_data

def test_fetch_irs_data(sample_page_html):
    """
    Test sample_page_html is of type bytes and not empty.
    """
    assert isinstance(sample_page_html, bytes), "Fetched content should be of type bytes."
    assert len(sample_page_html) > 0, "Fetched content should not be empty."

def test_fetch_irs_data_status_code(sample_page_html):
    """
    Test the fetched content is a valid HTML response.
    """
    content = sample_page_html.decode('utf-8')
    assert content is not None, "Fetched content should not be None."
    # Check if the content is a valid HTML response
    assert "<html" in content.lower(), "Fetched content should be valid HTML."

def test_fetch_irs_data_content(sample_page_html):
    """
    Test that the fetched content contains expected keywords.
    """
    content = sample_page_html.decode('utf-8')
    assert "IRS" in content, "Fetched content should contain 'IRS'."
    assert "tax rates" in content.lower(), "Fetched content should contain 'tax rates'."
    assert "brackets" in content.lower(), "Fetched content should contain 'brackets'."
    assert "filing" in content.lower(), "Fetched content should contain 'filing'."
    assert "taxpayer" in content.lower(), "Fetched content should contain 'taxpayer'."
    assert "Married filing jointly" in content, "Fetched content should contain 'Married Filing Jointly'."
    assert "single" in content, "Fetched content should contain 'single'."
    assert "Head of household" in content, "Fetched content should contain 'Head of Household'."
    assert "Married filing separately" in content, "Fetched content should contain 'Married Filing Separately'."

if __name__ == "__main__":
    pytest.main()