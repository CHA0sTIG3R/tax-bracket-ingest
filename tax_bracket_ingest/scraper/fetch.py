# tax_bracket_ingest/scraper/fetch.py
IRS_URL = "https://www.irs.gov/filing/federal-income-tax-rates-and-brackets"

# fetch data from the IRS URL 
import requests
def fetch(url: str) -> bytes:
    """
    Fetch the content from the given URL.
    
    Args:
        url (str): The URL to fetch data from.
    Returns:
        bytes: The content of the response.
    Raises:
        requests.RequestException: If there is an error during the request.
    """
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.content

def fetch_irs_data() -> bytes:
    """
    Fetch the IRS data from the predefined URL.
    
    Returns:
        str: The content of the IRS data page.
    """
    return fetch(IRS_URL)
