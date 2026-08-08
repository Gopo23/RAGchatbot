# Implementation Plan: Mutual Fund FAQ Assistant

This document outlines the phase-wise implementation plan for building the RAG-based Facts-Only FAQ Assistant, strictly following the streamlined architecture that relies solely on the 5 approved Groww URLs.

## Phase 1: Project Setup & Scaffolding

**Goal:** Establish the foundational directory structure, environment, and dependencies.

1. **Initialize Project Structure:**
   - Create the directory hierarchy defined in the Architecture (e.g., `data/raw/groww`, `data/processed`, `embeddings`, `src/ingestion`, `src/retrieval`, `src/generation`, `src/ui`).
2. **Dependency Management:**
   - Create `requirements.txt` with necessary libraries: `requests`, `beautifulsoup4`, `langchain`, `chromadb`, `groq`, `sentence-transformers`, `streamlit`, `python-dotenv`.
3. **Configuration:**
   - Setup `.env` template for API keys (e.g., `GROQ_API_KEY`).
   - Create `config/settings.py` for global constants (chunk sizes, model names, target URLs).

## Phase 2: Data Ingestion Pipeline (Offline)

**Goal:** Scrape the 5 Groww fund pages, process the text, and store the embeddings in ChromaDB.

1. **Task 2.1: Implement Web Scraper (`src/ingestion/scraper.py`)**
   - Use `requests` to fetch raw HTML from the 5 configured Groww URLs.
   - Add simple retry logic and save the raw HTML files locally to `data/raw/groww/` for caching.
2. **Task 2.2: Implement HTML Parser & Cleaner**
   - Use `BeautifulSoup4` to extract the `__NEXT_DATA__` JSON payload from the raw HTML to prevent cross-fund hallucination (e.g., similar funds table).
   - Parse the `mfServerSideData` to extract specific, highly-structured real-time facts (AUM, expense ratio, exit load) and format it as clean text.
3. **Task 2.3: Implement Text Chunker (`src/ingestion/chunker.py`)**
   - Implement LangChain's `RecursiveCharacterTextSplitter` (1000 token chunks, 200 token overlap) with custom separators `["\n", ". ", " ", ""]` to prevent splitting dense key-value pairs.
   - Construct and attach metadata to each chunk (e.g., `source_url`, `fund_name`, `last_updated`).
4. **Task 2.4: Initialize BGE Embedder & Vector Store (`src/ingestion/embedder.py`)**
   - Load the BGE embedding model locally (`BAAI/bge-small-en-v1.5`) using `sentence-transformers`.
   - Initialize a local ChromaDB instance in the `embeddings/chroma_db/` directory.
5. **Task 2.5: Create the End-to-End Pipeline Script (`src/ingestion/pipeline.py`)**
   - Connect the Scraper, Cleaner, Chunker, and Embedder components together.
   - Execute the pipeline to process all 5 funds and verify they are successfully upserted into ChromaDB.

## Phase 3: RAG Query Engine & Refusal Logic

**Goal:** Build the online retrieval and LLM generation backend.

1. **Refusal Handler (`src/retrieval/refusal_handler.py`):**
   - Implement keyword/intent matching to intercept advisory, comparative, or predictive queries before they hit the LLM.
2. **Query Engine (`src/retrieval/query_engine.py`):**
   - Implement Maximal Marginal Relevance (MMR) search with `k=4` and `fetch_k=10` against ChromaDB to ensure highly relevant and diverse context.
   - Format retrieved chunks into a single context string along with their source URLs for citation.
3. **LLM Generation (`src/generation/`):**
   - **`prompt_builder.py`**: Construct the strict system prompt (max 3 sentences, mandatory citation).
   - **`llm_client.py`**: Connect to Groq's API (using `llama-3.3-70b-versatile`). Implement rate limit handling (exponential backoff) using `tenacity` to respect Groq's strict limits (30 RPM, 1K RPD, 12K TPM, 100K TPD).
   - **`response_formatter.py`**: Ensure the final output string correctly appends the source link and last updated footer.

## Phase 4: User Interface (Streamlit)

**Goal:** Provide a clean, minimal chat interface for users.

1. **Core Layout (`src/ui/app.py`):**
   - Set up the main Streamlit chat interface.
   - Add the persistent disclaimer banner ("Facts-only. No investment advice. This assistant only provides factual information from the official Groww mutual fund pages.").
2. **Interactive Elements:**
   - Add 3 clickable example queries to the sidebar or welcome screen.
   - Implement session state to handle the chat history visually.
   - Dynamically load and display a "Supported Funds" table in the sidebar that extracts the real-time expense ratio from the processed text files for all provided links.
3. **Backend Integration:**
   - Connect the chat input to the Refusal Handler and RAG Query Engine.
   - Stream or display the final response with the formatted citations.

## Phase 5: Automated Scheduler

**Goal:** Automate the data ingestion pipeline to ensure the vector store always has the latest mutual fund data using GitHub Actions.

1. **GitHub Actions Workflow (`.github/workflows/daily_ingestion.yml`):**
   - Create a GitHub Actions workflow triggered by a `schedule` event (cron expression) to run automatically every day at 10:30 AM IST (`0 5 * * *` UTC).
   - The workflow should check out the repository, set up the Python environment, install dependencies, and run `python src/ingestion/pipeline.py`.
2. **Commit and Push Updates:**
   - The workflow should commit and push the updated vector store and processed data back to the repository to ensure the live application always serves the freshest data.

---

## User Review Required

> [!IMPORTANT]
> - **Groq API Key**: This implementation plan uses Groq for LLM generation (`llama-3.3-70b-versatile`) and local BGE models for embeddings. You will need to provide a `GROQ_API_KEY` in the `.env` file once the scaffolding is set up.
> - **Local Embeddings**: The BGE embedding model (`BAAI/bge-small-en-v1.5`) will be downloaded and run locally.
> - **Local DB**: The vector database (ChromaDB) will be stored locally on your disk in the `embeddings/` folder to save costs and avoid external database hosting. 

## Verification Plan

### Automated Tests
- **Scraper Test:** Verify HTML extraction runs successfully for all 5 URLs.
- **RAG Unit Tests:** Send mock factual queries to verify context retrieval returns the correct chunks.
- **Refusal Tests:** Send known advisory queries (e.g., "Which is better?") to ensure the refusal handler intercepts them.

### Manual Verification
- Run the Streamlit app locally (`streamlit run src/ui/app.py`).
- Click through the example questions to verify end-to-end latency and response formatting.
- Verify the responses strictly adhere to the 3-sentence limit and include the source link.
