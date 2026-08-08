import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.ingestion.embedder import get_vectorstore

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def retrieve_context(query: str, k: int = 4, fetch_k: int = 10) -> tuple[str, list[dict]]:
    """
    Retrieves the most relevant chunks using Maximal Marginal Relevance (MMR).
    Returns a formatted context string and a list of metadata dictionaries for citations.
    """
    vectorstore = get_vectorstore()
    
    # Use MMR search to ensure relevance and diversity
    logging.info(f"Retrieving context for query: '{query}' using MMR (k={k}, fetch_k={fetch_k})")
    
    # In langchain Chroma, max_marginal_relevance_search takes k and fetch_k
    docs = vectorstore.max_marginal_relevance_search(query, k=k, fetch_k=fetch_k)
    
    if not docs:
        logging.warning("No documents retrieved from ChromaDB.")
        return "", []

    context_parts = []
    citations = []
    
    for i, doc in enumerate(docs):
        # Format the text
        context_parts.append(f"--- Chunk {i+1} ---\n{doc.page_content}\n")
        
        # Keep track of unique metadata for citations
        meta = doc.metadata
        source_url = meta.get("source_url", "Unknown URL")
        fund_name = meta.get("fund_name", "Unknown Fund")
        last_updated = meta.get("last_updated", "Unknown Date")
        
        citation_info = {
            "source_url": source_url,
            "fund_name": fund_name,
            "last_updated": last_updated
        }
        
        if citation_info not in citations:
            citations.append(citation_info)
            
    context_string = "\n".join(context_parts)
    return context_string, citations

if __name__ == "__main__":
    test_query = "What is the exit load for HDFC Gold ETF?"
    context, citations = retrieve_context(test_query)
    print("--- Retrieved Context ---")
    print(context)
    print("--- Citations ---")
    print(citations)
