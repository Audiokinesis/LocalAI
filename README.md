# Local Document Intelligence

A local-first RAG app for uploading PDF, Markdown, and TXT files, searching their contents, and extracting evidence-grounded insights with Ollama.

## Requirements

- Python 3.10+
- Ollama installed and running: https://ollama.com/
- Suggested models:
  ```bash
  ollama pull llama3.2
  ollama pull nomic-embed-text
  ```

The first model generates answers; the embedding model powers semantic search. Model downloads and Python package installation need internet access. After setup, processing can run locally.

## Start

### Windows
Double-click `run_windows.bat`. It creates a virtual environment, installs dependencies, and opens Streamlit.

### macOS / Linux
Run:
```bash
chmod +x run.sh
./run.sh
```

Then open the local URL printed by Streamlit, normally http://localhost:8501.

## Use the interface

1. In the sidebar, configure Ollama URL and model names if needed.
2. Click **Check Ollama connection**.
3. Open **Upload & Index**, upload PDF/MD/TXT, and click **Save and index selected files**.
4. Open **Ask / Extract Wisdom** to ask a question or extract insights.
5. Open **Document Library** to see indexed files and remove their chunks from search.

## Local storage

- Uploaded originals: `data/documents/`
- Persistent Chroma database: `data/chroma/`

Back up both folders if you want to preserve originals and the index. The index can be rebuilt from the originals.

## Notes and limitations

- Text-based PDFs are supported. Scanned/image-only PDFs require OCR, which this initial version does not include.
- Chunking is recursive and overlap-based, designed to preserve nearby context. Chunk size and overlap are configurable in the sidebar.
- Search uses cosine distance. A lower distance generally means a closer vector match; it is not a calibrated confidence score.
- Source page mapping is best-effort for PDFs. TXT/Markdown source references may not have meaningful page numbers.
- If you change the embedding model after indexing, re-index your documents into a fresh Chroma database; vectors from different embedding models must not be mixed.
- This is a starter implementation. For sensitive decisions, verify conclusions against the cited passages.
- Keep Ollama bound to localhost and do not expose it to untrusted networks.
