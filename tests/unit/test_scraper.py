import pytest
from tax_bracket_ingest.scraper.fetch import fetch_irs_data

# You can set scope="module" to call the function once per test module run.
@pytest.fixture(scope="module")
def fetched_content():
    return fetch_irs_data()

def test_fetch_irs_data(fetched_content):
    """
    Test fetched_content is of type bytes and not empty.
    """
    assert isinstance(fetched_content, bytes), "Fetched content should be of type bytes."
    assert len(fetched_content) > 0, "Fetched content should not be empty."

def test_fetch_irs_data_status_code(fetched_content):
    """
    Test the fetched content is a valid HTML response.
    """
    content = fetched_content.decode('utf-8')
    assert content is not None, "Fetched content should not be None."
    # Check if the content is a valid HTML response
    assert "<html" in content.lower(), "Fetched content should be valid HTML."

def test_fetch_irs_data_content(fetched_content):
    """
    Test that the fetched content contains expected keywords.
    """
    content = fetched_content.decode('utf-8')
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