from __future__ import annotations
import chromadb
from src.config import CHROMA_DIR, COLLECTION_NAME
from src.ollama_client import embed_texts


class LocalKnowledgeStore:
    def __init__(self, host: str, embedding_model: str):
        self.host = host
        self.embedding_model = embedding_model
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={'hnsw:space': 'cosine'},
        )

    def count(self) -> int:
        return self.collection.count()

    def add_chunks(self, chunks: list[dict], batch_size: int = 32) -> int:
        if not chunks:
            return 0
        added = 0
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]
            vectors = embed_texts(self.host, self.embedding_model, [x['text'] for x in batch])
            self.collection.upsert(
                ids=[x['id'] for x in batch],
                documents=[x['text'] for x in batch],
                metadatas=[x['metadata'] for x in batch],
                embeddings=vectors,
            )
            added += len(batch)
        return added

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        total = self.collection.count()
        if total == 0:
            return []
        vector = embed_texts(self.host, self.embedding_model, [question])[0]
        result = self.collection.query(
            query_embeddings=[vector],
            n_results=min(top_k, total),
            include=['documents', 'metadatas', 'distances'],
        )
        docs = result.get('documents', [[]])[0] or []
        metas = result.get('metadatas', [[]])[0] or []
        distances = result.get('distances', [[]])[0] or []
        return [
            {'text': docs[i], 'metadata': metas[i] or {}, 'distance': float(distances[i])}
            for i in range(len(docs))
        ]

    def delete_source(self, source_id: str) -> None:
        self.collection.delete(where={'source_id': source_id})

    def clear(self) -> None:
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={'hnsw:space': 'cosine'},
        )

    def list_sources(self) -> list[dict]:
        if self.count() == 0:
            return []
        result = self.collection.get(include=['metadatas'])
        grouped = {}
        for meta in result.get('metadatas', []) or []:
            if not meta or not meta.get('source_id'):
                continue
            sid = meta['source_id']
            item = grouped.setdefault(sid, {
                'source_id': sid,
                'file_name': meta.get('file_name', sid),
                'file_type': meta.get('file_type', ''),
                'chunks': 0,
            })
            item['chunks'] += 1
        return sorted(grouped.values(), key=lambda x: x['file_name'].lower())
