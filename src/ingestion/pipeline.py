import logging
from pathlib import Path
import sys

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.ingestion.scraper import run_scraper
from src.ingestion.cleaner import run_cleaner
from src.ingestion.chunker import create_chunks_from_files
import importlib
import src.ingestion.embedder
importlib.reload(src.ingestion.embedder)
from src.ingestion.embedder import store_chunks, reset_vectorstore

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_pipeline():
    logging.info("=== Starting Groww Mutual Fund Ingestion Pipeline ===")
    
    # 1. Scrape
    logging.info("\n--- Phase 1: Web Scraping ---")
    run_scraper()
    
    # 2. Clean
    logging.info("\n--- Phase 2: HTML Cleaning ---")
    run_cleaner()
    
    # 3. Chunk
    logging.info("\n--- Phase 3: Text Chunking ---")
    documents = create_chunks_from_files()
    if not documents:
        logging.error("No chunks were created. Aborting pipeline.")
        return
        
        
    # 4. Embed & Store
    logging.info("\n--- Phase 4: Embedding and Vector Storage ---")
    reset_vectorstore()
    store_chunks(documents)
    
    logging.info("\n=== Ingestion Pipeline Completed Successfully! ===")

if __name__ == "__main__":
    run_pipeline()
