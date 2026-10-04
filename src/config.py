from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
DOCUMENTS_DIR = DATA_DIR / 'documents'
CHROMA_DIR = DATA_DIR / 'chroma'
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_CHAT_MODEL = os.getenv('RAG_CHAT_MODEL', 'llama3.2')
DEFAULT_EMBED_MODEL = os.getenv('RAG_EMBED_MODEL', 'nomic-embed-text')
DEFAULT_OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 180
DEFAULT_TOP_K = 5
COLLECTION_NAME = 'local_document_intelligence_v2'
SUPPORTED_EXTENSIONS = {'.pdf', '.md', '.txt'}
