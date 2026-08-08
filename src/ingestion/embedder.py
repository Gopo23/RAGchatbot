import os
import logging
from pathlib import Path
import sys

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from config.settings import EMBEDDING_MODEL_NAME

# Langchain imports
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Vector DB location
CHROMA_PERSIST_DIR = PROJECT_ROOT / "embeddings" / "chroma_db"

def get_embedder():
    """Initializes and returns the BGE Embedder."""
    logging.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    
    # BGE specific kwargs
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True} # BGE models require normalization for cosine similarity
    
    embedder = HuggingFaceBgeEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    return embedder

def get_vectorstore():
    """Returns the Chroma vectorstore instance."""
    embedder = get_embedder()
    
    # Note: latest Chroma in langchain automatically handles persistence via persist_directory
    vectorstore = Chroma(
        collection_name="groww_funds",
        embedding_function=embedder,
        persist_directory=str(CHROMA_PERSIST_DIR)
    )
    return vectorstore

def store_chunks(documents: list[Document]):
    """Stores a list of documents into ChromaDB."""
    if not documents:
        logging.warning("No documents provided to store in ChromaDB.")
        return
        
    logging.info(f"Initializing VectorStore and storing {len(documents)} chunks...")
    
    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents)
    
    logging.info(f"Successfully stored {len(documents)} chunks in ChromaDB at {CHROMA_PERSIST_DIR}")

def reset_vectorstore():
    """Deletes the existing Chroma collection to prevent duplicates on re-ingestion."""
    logging.info("Resetting VectorStore (deleting existing collection)...")
    try:
        vectorstore = get_vectorstore()
        vectorstore.delete_collection()
    except Exception as e:
        logging.warning(f"Failed to delete collection (might not exist yet): {e}")

if __name__ == "__main__":
    # Test initialization
    logging.info("Testing BGE Embedder initialization...")
    embedder = get_embedder()
    test_embedding = embedder.embed_query("What is the NAV of HDFC Gold ETF?")
    logging.info(f"Test embedding generated successfully! Dimension: {len(test_embedding)}")
