import os
import logging
from pathlib import Path
from bs4 import BeautifulSoup
import sys

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

import json

def clean_html(html_content: str) -> str:
    """Parses HTML and extracts clean, readable text using NextJS server side data if available."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    script = soup.find('script', id='__NEXT_DATA__')
    if script:
        try:
            data = json.loads(script.string)
            mf_data = data.get('props', {}).get('pageProps', {}).get('mfServerSideData', {})
            if mf_data:
                lines = []
                lines.append(f"Fund Name: {mf_data.get('scheme_name')}")
                lines.append(f"Expense ratio {mf_data.get('expense_ratio')}%")
                lines.append(f"Exit load: {mf_data.get('exit_load')}")
                lines.append(f"Category: {mf_data.get('category')} - {mf_data.get('sub_category')}")
                lines.append(f"AUM: {mf_data.get('aum')} Cr")
                lines.append(f"Minimum SIP Investment: {mf_data.get('min_sip_investment')}")
                lines.append(f"Lock-in period: {mf_data.get('lock_in', 'No lock-in')}")
                lines.append(f"Risk: {mf_data.get('risk')}")
                lines.append(f"Benchmark: {mf_data.get('benchmark_name')}")
                lines.append(f"Fund Manager: {mf_data.get('fund_manager')}")
                lines.append(f"Launch Date: {mf_data.get('launch_date')}")
                lines.append(f"Stamp Duty: {mf_data.get('stamp_duty')}")
                if mf_data.get('description'):
                    lines.append(f"Description: {mf_data.get('description')}")
                
                return "\n".join(lines)
        except Exception as e:
            logging.error(f"Error parsing JSON: {e}")

    # Fallback to unstructured text extraction
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()
        
    text = soup.get_text(separator=' ')
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)
    
    # Truncate the massive Groww footer if it exists
    footer_markers = [
        "Contact Us Download the App",
        "Share Market Indices",
        "Top Gainers Stocks"
    ]
    for marker in footer_markers:
        idx = cleaned_text.find(marker)
        if idx != -1:
            cleaned_text = cleaned_text[:idx].strip()
            break
            
    return cleaned_text

def run_cleaner():
    """Reads raw HTML files, cleans them, and saves to processed directory."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if not RAW_DATA_DIR.exists():
        logging.error(f"Raw data directory {RAW_DATA_DIR} does not exist.")
        return
        
    html_files = list(RAW_DATA_DIR.glob("*.html"))
    if not html_files:
        logging.warning("No HTML files found to process.")
        return
        
    success_count = 0
    for file_path in html_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
                
            cleaned_text = clean_html(html_content)
            
            output_path = PROCESSED_DATA_DIR / f"{file_path.stem}.txt"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(cleaned_text)
                
            logging.info(f"Cleaned and saved to {output_path}")
            success_count += 1
        except Exception as e:
            logging.error(f"Failed to clean {file_path.name}: {e}")
            
    logging.info(f"Cleaning completed. {success_count}/{len(html_files)} successful.")

if __name__ == "__main__":
    run_cleaner()
