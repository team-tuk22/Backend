import os, httpx

BASE_URL = os.getenv("CRAWL_BASE_URL")

def fetch_law_data(law_id: str):
    if not BASE_URL:
        raise RuntimeError("CRAWL_BASE_URL is not set")
    url = f"{BASE_URL}{law_id}"
    resp = httpx.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()
