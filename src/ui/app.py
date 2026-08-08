import sys

# Streamlit Cloud uses an older SQLite version unsupported by ChromaDB. 
# This overrides it with the newer pysqlite3-binary.
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

from pathlib import Path
import streamlit as st

# Add project root to sys.path so we can import local modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import the RAG components
from src.retrieval.refusal_handler import is_advisory_query, get_refusal_message
from src.retrieval.query_engine import retrieve_context
from src.generation.prompt_builder import build_prompt
from src.generation.llm_client import generate_response
from src.generation.response_formatter import format_final_response

# Basic Streamlit Config
st.set_page_config(page_title="Groww Mutual Fund FAQ", page_icon="📈", layout="centered")

def init_session_state():
    """Initialize chat history in Streamlit session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
def main():
    st.title("Groww Mutual Fund FAQ Assistant")
    
    # Persistent Disclaimer Banner
    st.info("⚠️ **Disclaimer:** Facts-only. No investment advice. This assistant only provides factual information from the official Groww mutual fund pages.")
    
    init_session_state()
    
    # Sidebar - Interactive Elements
    with st.sidebar:
        st.header("Admin")
        if st.button("🔄 Refresh Fund Data"):
            with st.spinner("Scraping and updating vector store (this may take a minute)..."):
                from src.ingestion.pipeline import run_pipeline
                run_pipeline()
            st.success("Data refreshed successfully! Latest data fetched.")
            
        st.divider()
        
        st.header("Example Queries")
        st.write("Click any example to quickly ask the assistant:")
        
        example_queries = [
            "What is the exit load for HDFC Gold ETF?",
            "What is the NAV of HDFC Large Cap Fund?",
            "What is the expense ratio of HDFC Small Cap Fund?"
        ]
        
        for q in example_queries:
            if st.button(q):
                st.session_state.example_query = q
                
        st.divider()
        
        st.header("Supported Funds")
        
        # Real-time extraction of expense ratio from processed data
        import re
        from config.settings import PROCESSED_DATA_DIR, GROWW_URLS
        from src.ingestion.scraper import get_slug_from_url
        
        funds_table = "| Fund Name | Expense Ratio |\n|---|---|\n"
        for url in GROWW_URLS:
            slug = get_slug_from_url(url)
            txt_path = PROCESSED_DATA_DIR / f"{slug}.txt"
            expense_ratio = "N/A"
            fund_name = slug.replace("-", " ").title()
            
            if txt_path.exists():
                with open(txt_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    match = re.search(r'Expense ratio\s+(\d+\.\d+%)', content)
                    if match:
                        expense_ratio = match.group(1)
            
            funds_table += f"| {fund_name} | {expense_ratio} |\n"
            
        st.markdown(funds_table)

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Determine if input comes from chat bar or a clicked example query
    user_input = st.chat_input("Ask a question about the funds...")
    
    if hasattr(st.session_state, 'example_query') and st.session_state.example_query:
        user_input = st.session_state.example_query
        st.session_state.example_query = None # Reset so it doesn't loop
        
    # Handle the Input
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
            
        # Add to session state
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Process and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Fetching facts..."):
                
                # Step 1: Check for refusal (Advisory queries)
                if is_advisory_query(user_input):
                    final_response = get_refusal_message()
                else:
                    # Step 2: Retrieve Context from ChromaDB
                    context, citations = retrieve_context(user_input)
                    
                    if not context:
                        final_response = "I couldn't find any relevant factual information for your query in the provided Groww mutual fund data."
                    else:
                        # Step 3: LLM Generation
                        llm_prompt = build_prompt(user_input, context)
                        raw_response = generate_response(llm_prompt)
                        final_response = format_final_response(raw_response, citations)
                
            st.markdown(final_response)
        
        # Save assistant response to session state
        st.session_state.messages.append({"role": "assistant", "content": final_response})

if __name__ == "__main__":
    main()
