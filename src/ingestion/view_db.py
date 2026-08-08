import logging
from pathlib import Path
import sys

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.ingestion.embedder import get_vectorstore

def view_database():
    print("Loading ChromaDB...")
    vectorstore = get_vectorstore()
    
    # Access the underlying chromadb collection to fetch everything
    collection = vectorstore._collection
    Write a basic script so that I can view embeddings for these chunks (VERIFY ALL THE EMBEDDINGs)
    print(f"\nTotal chunks in DB: {collection.count()}")
    
    # Fetch the first 2 items with embeddings
    results = collection.get(
        limit=2,Write a basic script so that I can view embeddings for these chunks (VERIFY ALL THE EMBEDDINGs)
        include=["embeddings", "metadatas", "documents"]
    )
    
    print("\n=== SAMPLE CHUNKS ===")
    for i in range(len(results['ids'])):
        print(f"\n--- Chunk {i+1} ---")
        print(f"ID: {results['ids'][i]}")
        print(f"Metadata: {results['metadatas'][i]}")
        print(f"Document snippet (first 100 chars): {results['documents'][i][:100].strip()}...")
        
        embedding = results['embeddings'][i]
        print(f"Embedding dimensions: {len(embedding)}")
        print(f"Embedding preview: {[round(e, 4) for e in embedding[:5]]} ... (truncated)")

if __name__ == "__main__":
    # Suppress verbose logging from sentence-transformers for clean output
    logging.getLogger().setLevel(logging.ERROR)
    view_database()
