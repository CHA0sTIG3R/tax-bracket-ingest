# tax_bracket_ingest/scraper/fetch.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


IRS_URL = "https://www.irs.gov/filing/federal-income-tax-rates-and-brackets"


class FetchError(RuntimeError):
    """Raised when retrieving IRS data fails."""


_DEFAULT_TIMEOUT = 10
_MAX_RETRIES = Retry(
    total=3,
    status_forcelist=(429, 500, 502, 503, 504),
    backoff_factor=0.5,
    allowed_methods=("GET",),
)
_HEADERS = {
    "User-Agent": "tax-bracket-ingest/1.0 (+https://www.irs.gov/)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
_SESSION = requests.Session()
_SESSION.mount("https://", HTTPAdapter(max_retries=_MAX_RETRIES))
_SESSION.mount("http://", HTTPAdapter(max_retries=_MAX_RETRIES))


def _format_body_snippet(body: str, limit: int = 200) -> str:
    """Condense response text into a diagnostic snippet."""
    condensed = " ".join(body.split())
    if len(condensed) <= limit:
        return condensed
    return f"{condensed[:limit]}..."


def fetch(url: str, timeout: float = _DEFAULT_TIMEOUT) -> bytes:
    """Fetch a URL with retries, timeout, and diagnostic error reporting."""
    try:
        response = _SESSION.get(url, timeout=timeout, headers=_HEADERS)
    except requests.RequestException as exc:
        raise FetchError(f"Request to {url} failed: {exc}") from exc

    if response.status_code != 200:
        snippet = _format_body_snippet(response.text)
        raise FetchError(
            f"GET {url} returned {response.status_code} {response.reason}: {snippet}"
        )

    return response.content


def fetch_irs_data() -> bytes:
    """Fetch the IRS tax bracket page contents."""
    return fetch(IRS_URL)
