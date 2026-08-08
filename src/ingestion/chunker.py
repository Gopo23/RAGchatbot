import os
import logging
import json
from pathlib import Path
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import sys

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from config.settings import PROCESSED_DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP, GROWW_URLS

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_url_from_slug(slug: str) -> str:
    """Matches a filename slug back to its official Groww URL."""
    for url in GROWW_URLS:
        if url.endswith(slug):
            return url
    return f"https://groww.in/mutual-funds/{slug}"

def get_fund_name_from_slug(slug: str) -> str:
    """Creates a readable fund name from the slug."""
    # hdfc-gold-etf-fund-of-fund-direct-plan-growth -> Hdfc Gold Etf Fund Of Fund Direct Plan Growth
    words = slug.split("-")
    # Custom rule for HDFC to be uppercase
    words = ["HDFC" if word.lower() == "hdfc" else word.capitalize() for word in words]
    return " ".join(words)

def create_chunks_from_files() -> list[Document]:
    """Reads all processed text files, chunks them, and attaches metadata."""
    
    if not PROCESSED_DATA_DIR.exists():
        logging.error(f"Processed data directory {PROCESSED_DATA_DIR} does not exist.")
        return []
        
    txt_files = list(PROCESSED_DATA_DIR.glob("*.txt"))
    if not txt_files:
        logging.warning("No processed text files found to chunk.")
        return []
        
    # We use RecursiveCharacterTextSplitter with the updated strategy
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n", ". ", " ", ""],
        length_function=len, # Using char length roughly equivalent to our 1000 'token' strategy for simplicity
        is_separator_regex=False
    )
    
    all_documents = []
    
    for file_path in txt_files:
        slug = file_path.stem
        source_url = get_url_from_slug(slug)
        fund_name = get_fund_name_from_slug(slug)
        last_updated = datetime.now().strftime("%Y-%m-%d")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text_content = f.read()
                
            metadata = {
                "source_url": source_url,
                "fund_name": fund_name,
                "last_updated": last_updated
            }
            
            # Langchain's create_documents accepts lists of texts and lists of metadatas
            docs = text_splitter.create_documents([text_content], metadatas=[metadata])
            all_documents.extend(docs)
            
            logging.info(f"Chunked {slug}: created {len(docs)} chunks.")
        except Exception as e:
            logging.error(f"Failed to chunk {file_path.name}: {e}")
            
    logging.info(f"Total chunks created across all files: {len(all_documents)}")
    return all_documents

if __name__ == "__main__":
    docs = create_chunks_from_files()
    if docs:
        logging.info("Sample chunk metadata:")
        logging.info(docs[0].metadata)
        logging.info(f"Sample chunk text length: {len(docs[0].page_content)} chars")
