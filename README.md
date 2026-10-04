# 📚 Local Document Intelligence

### Private, Local-First Retrieval-Augmented Generation with Python, Ollama & ChromaDB

A production-minded **Retrieval-Augmented Generation (RAG)** application that allows users to upload documents, build a local semantic knowledge base, and ask questions that are answered using retrieved evidence from the indexed documents.

The application is built around a local-first architecture using **Python, Streamlit, Ollama, and ChromaDB**.

> **Upload → Index → Retrieve → Ask → Inspect Evidence**

When Ollama is running locally, document processing, embeddings, vector storage, retrieval, and LLM inference can remain within the local environment.

---

## 🎯 What This Project Demonstrates

This project goes beyond a basic chatbot interface by implementing an end-to-end RAG pipeline:

```text
Documents
    ↓
Text Extraction
    ↓
Deterministic Chunking
    ↓
Embeddings
    ↓
ChromaDB
    ↓
Semantic Retrieval
    ↓
Grounded Prompt
    ↓
Local LLM
    ↓
Answer + Evidence
```

The application provides a complete interface for managing the knowledge base, configuring Ollama models, indexing documents, querying the knowledge base, and inspecting retrieved evidence.

---

## 🛠️ Built With

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python\&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Application-FF4B4B?logo=streamlit\&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-black)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Database-orange)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-PDF%20Extraction-blue)
![pypdf](https://img.shields.io/badge/pypdf-PDF%20Processing-green)

### Technology Stack

| Technology | Role                              |
| ---------- | --------------------------------- |
| Python     | Application and RAG pipeline      |
| Streamlit  | Web interface                     |
| Ollama     | Local LLM and embedding inference |
| ChromaDB   | Persistent vector database        |
| PyMuPDF    | PDF text extraction               |
| pypdf      | PDF extraction fallback           |

Default models:

| Model              | Purpose                       |
| ------------------ | ----------------------------- |
| `llama3.2`         | Chat / answer generation      |
| `nomic-embed-text` | Document and query embeddings |

---

# ✨ Key Features

### 📄 Multi-Format Document Ingestion

Supports:

* PDF
* Markdown
* TXT

PDF extraction uses **PyMuPDF with pypdf fallback**.

The application detects files that produce no extractable text, making it clear when a scanned/image-only PDF requires OCR.

---

### 🧩 Deterministic Recursive Chunking

Documents are split using a configurable recursive chunking strategy.

```text
Paragraph
    ↓
Newline
    ↓
Sentence
    ↓
Semicolon
    ↓
Comma
    ↓
Whitespace
    ↓
Fixed-length fallback
```

Configurable parameters include:

* Chunk size
* Chunk overlap
* Number of retrieved chunks

Default configuration:

```text
Chunk size:      1000 characters
Chunk overlap:    180 characters
Retrieved chunks: 5
```

---

### 🔑 SHA-256 Document Identification

Each uploaded document receives a deterministic SHA-256 identifier based on its original bytes.

This provides a stable source identity for:

* Re-indexing
* Document deletion
* Chunk association
* Source tracking

Documents are stored using the generated identifier rather than relying solely on their original filename.

---

### 🧠 Semantic Search with ChromaDB

The application converts both documents and questions into embeddings.

When a user asks a question:

```text
Question
   ↓
Embedding
   ↓
ChromaDB
   ↓
Similarity Search
   ↓
Top-K Evidence
```

The retrieved chunks are then provided to the LLM as contextual evidence.

---

### 🎯 Evidence-Grounded Answers

The RAG pipeline is designed to reduce unsupported generation by instructing the model to:

* Use retrieved evidence.
* Avoid inventing facts.
* Avoid inventing citations.
* Distinguish evidence from inference.
* Identify disagreements between sources.
* Acknowledge insufficient evidence.

The UI then exposes the retrieved evidence behind the answer.

---

### 🔎 Evidence Inspection

Users can inspect each retrieved result, including:

* Source filename
* Page number where available
* Chunk excerpt
* ChromaDB distance score

This provides transparency into **what information the model actually received**.

---

### 🗂️ Knowledge Library

The application provides a simple document-management interface for:

* Viewing indexed documents
* Viewing chunk counts
* Removing individual documents
* Clearing the entire vector index

---

### ⚙️ Dynamic Ollama Model Discovery

The UI queries Ollama to discover installed models rather than assuming a model is available.

Users can:

* View installed models
* Select chat models
* Select embedding models
* Refresh the model list
* Pull/install models from the interface
* Test the Ollama connection

This prevents a common local-AI failure mode where the application assumes a model exists when it has not been downloaded.

---

### 🩺 Built-In Diagnostics

The application includes a diagnostics interface showing:

* Ollama connection status
* Available models
* Chat model availability
* Embedding model availability
* ChromaDB location
* Document storage location
* Collection name
* Indexed chunk count

---

# 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │     Streamlit UI     │
                         └──────────┬───────────┘
                                    │
                       Upload / Question
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Document Pipeline  │
                         │                      │
                         │ PDF / MD / TXT       │
                         │ Text Extraction      │
                         │ SHA-256 ID           │
                         │ Recursive Chunking   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       Ollama         │
                         │                      │
                         │ nomic-embed-text     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      ChromaDB        │
                         │                      │
                         │ Persistent Vectors   │
                         │ Cosine Similarity    │
                         │ Source Metadata      │
                         └──────────┬───────────┘
                                    │
                              User Question
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Semantic Retrieval   │
                         │                      │
                         │ Top-K Evidence       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Grounded Prompt     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       Ollama         │
                         │      llama3.2        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Answer + Evidence    │
                         └──────────────────────┘
```

---

# 📁 Project Structure

```text
local-document-intelligence/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── run.sh
├── run_windows.bat
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── documents.py
│   ├── ollama_client.py
│   ├── rag.py
│   └── store.py
│
└── data/
    ├── documents/
    │   └── .gitkeep
    │
    └── chroma/
        └── .gitkeep
```

### Module Responsibilities

| Module             | Responsibility                                                     |
| ------------------ | ------------------------------------------------------------------ |
| `app.py`           | Streamlit application and user workflow                            |
| `config.py`        | Paths, models, and application configuration                       |
| `documents.py`     | Extraction, hashing, validation, and chunking                      |
| `ollama_client.py` | Ollama connectivity, model discovery, embeddings, and chat         |
| `rag.py`           | Retrieval and grounded answer generation                           |
| `store.py`         | ChromaDB persistence, indexing, searching, and document management |

---

# 🚀 Quick Start

## Prerequisites

Install:

* Python 3.10+
* Ollama

Verify Python:

```powershell
python --version
```

Verify Ollama:

```powershell
ollama --version
```

---

## 1. Clone the Repository

```powershell
git clone https://github.com/YOUR_USERNAME/local-document-intelligence.git
cd local-document-intelligence
```

---

## 2. Create a Virtual Environment

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
py -m venv .venv
.venv\Scripts\activate.bat
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Install Ollama Models

```powershell
ollama pull llama3.2
ollama pull nomic-embed-text
```

Verify:

```powershell
ollama list
```

---

## 5. Start the Application

```powershell
streamlit run app.py
```

Or on Windows:

```cmd
run_windows.bat
```

Or macOS/Linux:

```bash
./run.sh
```

The application will be available at:

```text
http://localhost:8501
```

---

# 🖥️ Using the Application

## 1. Add Documents

Open:

**1 · Add Documents**

Upload one or more:

```text
PDF
MD
TXT
```

Then select:

**Save and Index Selected Documents**

The application will:

```text
Upload
  ↓
Generate SHA-256 Source ID
  ↓
Extract Text
  ↓
Create Chunks
  ↓
Generate Embeddings
  ↓
Store in ChromaDB
```

---

## 2. Ask Questions

Open:

**2 · Ask / Extract Wisdom**

Enter a question about the indexed documents.

The application performs:

```text
Question
   ↓
Query Embedding
   ↓
ChromaDB Similarity Search
   ↓
Top-K Retrieved Chunks
   ↓
Grounded Prompt
   ↓
Ollama
   ↓
Answer
```

---

## 3. Inspect Evidence

Retrieved evidence is displayed underneath the generated answer.

Each result can expose:

```text
Source
Page
Distance
Excerpt
```

This allows the user to inspect the underlying information rather than treating the generated answer as a black box.

---

# 🔐 Privacy & Security

The application follows a **local-first architecture**.

When Ollama is configured to run locally:

```text
Documents
    ↓
Local Application
    ↓
Local Embeddings
    ↓
Local ChromaDB
    ↓
Local LLM
```

No external AI API is required.

However, privacy depends on the configured Ollama endpoint. If Ollama is pointed at a remote server, document-related inference traffic may leave the local machine.

The repository intentionally excludes:

```text
Uploaded documents
ChromaDB database files
Environment variables
Secrets
Virtual environments
Python cache files
```

---

# ⚙️ Configuration

The application supports environment-variable overrides:

```text
RAG_CHAT_MODEL
RAG_EMBED_MODEL
OLLAMA_HOST
```

Example:

### PowerShell

```powershell
$env:RAG_CHAT_MODEL="llama3.2"
$env:RAG_EMBED_MODEL="nomic-embed-text"
$env:OLLAMA_HOST="http://localhost:11434"
```

---

# ⚠️ Current Limitations

### OCR

Scanned or image-only PDFs are not currently OCR'd.

### Embedding Model Changes

If the embedding model changes, the existing vector index should be cleared and the documents re-indexed.

### Multi-User Security

The current application is designed as a local application rather than a multi-user SaaS platform.

Production deployment would require authentication, authorization, tenant isolation, and access controls.

### Retrieval Evaluation

The current system exposes similarity results but does not yet implement a formal retrieval-quality evaluation framework.

---

# 🔮 Production Evolution

The current architecture can evolve toward a larger AI platform:

```text
Current Application

Streamlit
    │
    ├── Document Processing
    ├── ChromaDB
    └── Ollama


Potential Production Architecture

Web Application
       │
       ▼
    API Layer
       │
       ├── Authentication
       ├── Authorization
       ├── Document Service
       ├── Retrieval Service
       └── AI Service
              │
              ├── Vector Database
              ├── Object Storage
              └── LLM Infrastructure
```

Potential future capabilities include:

* OCR
* Authentication
* Multi-user support
* Document versioning
* Background indexing
* Retrieval evaluation
* Automated testing
* Observability
* Containerization
* CI/CD
* Cloud deployment
* Role-based access control

---

# 💼 Why This Project Matters

This project demonstrates practical implementation of an AI application rather than simply calling an LLM API.

It combines:

* Python application architecture
* RAG pipeline design
* Local LLM inference
* Vector databases
* Embedding generation
* Semantic retrieval
* Document processing
* Deterministic chunking
* Persistent storage
* Metadata management
* Defensive error handling
* Runtime model discovery
* Evidence-grounded generation
* Streamlit application development
* Security-conscious local AI architecture

The key engineering pattern is the separation of concerns between:

```text
Document Ingestion
        ↓
Vector Storage
        ↓
Retrieval
        ↓
LLM Generation
        ↓
User Interface
```

This creates a foundation that can be extended from a local prototype into a production AI system.

---

# 📜 License

Add an appropriate open-source license before publishing.

MIT or Apache-2.0 are common choices for publicly shared software.
