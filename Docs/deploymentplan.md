# Deployment Plan: Streamlit Community Cloud

This document outlines the strategy for deploying the RAG-based Mutual Fund FAQ Assistant on Streamlit Community Cloud. Because Streamlit handles both the frontend UI and the Python backend execution natively, we can deploy the entire application as a single unified service.

## 1. Overview

- **Hosting Platform**: Streamlit Community Cloud (Free Tier)
- **Source of Truth**: GitHub Repository (`main` branch)
- **Entry Point**: `src/ui/app.py`
- **Data Updates**: The GitHub Actions scheduler updates the local ChromaDB vector store and pushes it to GitHub. Streamlit automatically detects these commits and pulls the latest data seamlessly.

## 2. Prerequisites

1. **GitHub Repository**: The code is already pushed to `https://github.com/Gopo23/RAG-Chatbot`.
2. **Streamlit Account**: An account on [share.streamlit.io](https://share.streamlit.io/), linked to your GitHub account.
3. **API Keys**: You must have your `GROQ_API_KEY` ready to add to Streamlit's Secrets manager.

## 3. Step-by-Step Deployment Guide

### Step 1: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
2. Click **"New app"** in the top right corner.
3. Fill in the deployment details:
   - **Repository**: `Gopo23/RAG-Chatbot`
   - **Branch**: `main`
   - **Main file path**: `src/ui/app.py`
4. Click **Deploy!**

### Step 2: Configure Environment Secrets
Since `.env` is (correctly) ignored by git, Streamlit will not have your Groq API key initially, and the app will show an error until configured.
1. Once deployed, click the **three dots (⋮)** in the top right corner of your Streamlit app and select **"Settings"**.
2. Navigate to the **"Secrets"** tab.
3. Add your environment variables in TOML format:
   ```toml
   GROQ_API_KEY = "your-actual-api-key-here"
   ```
4. Click **Save**. The app will automatically reboot, read the key, and connect to the Groq API.

## 4. How the Architecture Works in the Cloud

- **Backend & Frontend Unified**: Both run within the same Streamlit Linux container.
- **Data Persistence**: Because Streamlit apps can sleep and spin down, the SQLite database (`chroma.sqlite3`) stored in `embeddings/` acts as the read-only knowledge base during runtime. 
- **Automated Data Syncing**: When your GitHub Actions workflow runs the ingestion pipeline every day at 10:30 AM IST and pushes a new commit to `main`, Streamlit Cloud automatically detects the new commit, restarts the container, and serves the app using the freshest data.

## 5. Known Limitations & Troubleshooting

- **ChromaDB SQLite Version Issue**: Streamlit Community Cloud runs an older version of Debian, which sometimes has an outdated `sqlite3` version that `chromadb` might complain about during deployment. 
  - *Fix (if encountered)*: You can add `pysqlite3-binary` to your `requirements.txt` and add these 3 lines to the very top of `src/ui/app.py` before any other imports:
    ```python
    import sys
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    ```
- **Memory Limits**: Streamlit Cloud provides ~1GB of RAM. Since we are using lightweight BGE embeddings locally and offloading the heavy 70B parameter LLM computation to Groq's external API, the application's memory footprint will remain well within safe limits.
- **Groq API Rate Limits**: The `llama-3.3-70b-versatile` model has strict rate limits (30 requests per minute, 1K requests per day, 12K tokens per minute, 100K tokens per day). Ensure your application handles these limits gracefully using retry logic or exponential backoff.
