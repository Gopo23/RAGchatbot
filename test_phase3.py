import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

# Load .env first since llm_client checks for it
load_dotenv()

from src.retrieval.refusal_handler import is_advisory_query, get_refusal_message
from src.retrieval.query_engine import retrieve_context
from src.generation.prompt_builder import build_prompt
from src.generation.llm_client import generate_response
from src.generation.response_formatter import format_final_response

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_query(query: str):
    print(f"\n{'='*50}\nTesting Query: '{query}'\n{'='*50}")
    
    if is_advisory_query(query):
        print("Refusal Triggered!")
        print(get_refusal_message())
        return
        
    context, citations = retrieve_context(query)
    if not context:
        print("No context retrieved!")
        return
        
    prompt = build_prompt(query, context)
    response_text = generate_response(prompt)
    final_response = format_final_response(response_text, citations)
    
    print("\n--- Final Response ---\n")
    print(final_response)
    print("\n" + "="*50)

if __name__ == "__main__":
    test_query("What is the exit load for HDFC Gold ETF?")
    test_query("Should I invest in HDFC Mid Cap Fund?")
    test_query("What is the NAV of HDFC Large Cap Fund?")
