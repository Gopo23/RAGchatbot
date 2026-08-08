import os
import requests
import time
import logging
from pathlib import Path
import sys

# Add project root to sys.path so we can import config
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from config.settings import GROWW_URLS, RAW_DATA_DIR

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_slug_from_url(url: str) -> str:
    """Extracts the slug from a Groww mutual fund URL to use as a filename."""
    # e.g., https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth
    return url.strip("/").split("/")[-1]

def fetch_html_with_retry(url: str, max_retries: int = 3, backoff_factor: int = 2) -> str:
    """Fetches HTML from a URL with simple retry logic."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            logging.info(f"Fetching {url} (Attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.warning(f"Failed to fetch {url}: {e}")
            if attempt < max_retries - 1:
                sleep_time = backoff_factor ** attempt
                logging.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logging.error(f"Max retries reached for {url}.")
                raise

def run_scraper():
    """Main function to scrape all configured URLs and save them."""
    # Ensure raw data directory exists
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    for url in GROWW_URLS:
        slug = get_slug_from_url(url)
        filepath = RAW_DATA_DIR / f"{slug}.html"
        
        # Always fetch the latest data (overwrite if exists)
        try:
            html_content = fetch_html_with_retry(url)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            logging.info(f"Successfully saved to {filepath}")
            success_count += 1
            # Polite delay between scraping different URLs
            time.sleep(2)
        except Exception as e:
            logging.error(f"Failed to process {url}: {e}")
            
    logging.info(f"Scraping completed. {success_count}/{len(GROWW_URLS)} successful.")

if __name__ == "__main__":
    run_scraper()
