import os
import sys
from pathlib import Path
import logging
from tenacity import retry, wait_exponential, stop_after_attempt

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from config.settings import LLM_MODEL_NAME, GROQ_API_KEY
from langchain_groq import ChatGroq

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_llm():
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in the environment variables.")
        
    return ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=LLM_MODEL_NAME,
        temperature=0.0, # Strictly factual
        max_tokens=256,  # 3 sentences max
        max_retries=2    # LangChain's built-in retries
    )

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(4),
    reraise=True
)
def invoke_llm_with_backoff(prompt: str):
    """
    Invokes the LLM with exponential backoff to handle Groq rate limits 
    (30 requests/min, 12k tokens/min).
    """
    llm = get_llm()
    return llm.invoke(prompt)

def generate_response(prompt: str) -> str:
    """
    Sends the prompt to the Groq LLM and returns the text response.
    """
    logging.info(f"Generating response using {LLM_MODEL_NAME} via Groq...")
    
    try:
        response = invoke_llm_with_backoff(prompt)
        return response.content
    except Exception as e:
        logging.error(f"Error generating response from LLM (Rate limits or API failure): {e}")
        return f"An error occurred while generating the response: {str(e)}\n\nThe system might be under heavy load or rate-limited. Please try again later."
