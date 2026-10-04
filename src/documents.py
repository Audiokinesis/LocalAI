from __future__ import annotations
import hashlib
from pathlib import Path
import fitz
from pypdf import PdfReader
from src.config import SUPPORTED_EXTENSIONS


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_file(path: Path) -> list[dict]:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f'Unsupported file type: {suffix or "(none)"}')
    records = []
    if suffix == '.pdf':
        try:
            with fitz.open(path) as pdf:
                for page_no, page in enumerate(pdf, start=1):
                    text = page.get_text('text').strip()
                    if text:
                        records.append({'text': text, 'page': page_no})
        except Exception:
            records = []
        if not records:
            try:
                reader = PdfReader(str(path))
                for page_no, page in enumerate(reader.pages, start=1):
                    text = (page.extract_text() or '').strip()
                    if text:
                        records.append({'text': text, 'page': page_no})
            except Exception as exc:
                raise ValueError(f'PDF extraction failed: {exc}') from exc
    else:
        text = path.read_text(encoding='utf-8-sig', errors='replace').strip()
        if text:
            records.append({'text': text, 'page': None})
    if not records:
        raise ValueError('No extractable text found. This may be a scanned/image-only PDF; OCR is not included yet.')
    return records


def split_text(text: str, chunk_size: int = 1000, overlap: int = 180) -> list[str]:
    if chunk_size < 100 or overlap < 0 or overlap >= chunk_size:
        raise ValueError('Chunk size must be >= 100 and overlap must be smaller than chunk size.')
    separators = ['\n\n', '\n', '. ', '? ', '! ', '; ', ', ', ' ']

    def recursive(value: str, level: int = 0) -> list[str]:
        value = value.strip()
        if not value:
            return []
        if len(value) <= chunk_size:
            return [value]
        if level >= len(separators):
            return [value[i:i + chunk_size] for i in range(0, len(value), chunk_size)]
        sep = separators[level]
        pieces = value.split(sep)
        if len(pieces) == 1:
            return recursive(value, level + 1)
        chunks, current = [], ''
        for piece in pieces:
            candidate = piece if not current else current + sep + piece
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current.strip())
                current = piece
        if current:
            chunks.append(current.strip())
        result = []
        for chunk in chunks:
            if len(chunk) > chunk_size:
                result.extend(recursive(chunk, level + 1))
            else:
                result.append(chunk)
        return result

    base = recursive(text)
    if overlap == 0 or len(base) < 2:
        return base
    output = []
    previous = ''
    for part in base:
        prefix = previous[-overlap:] if previous else ''
        merged = (prefix + '\n' + part).strip() if prefix else part
        if len(merged) > chunk_size:
            # Prefer keeping the new chunk intact; overlap is best-effort.
            merged = part
        if merged and (not output or merged != output[-1]):
            output.append(merged)
        previous = part
    return output


def prepare_chunks(path: Path, source_id: str, chunk_size: int, overlap: int) -> list[dict]:
    records = extract_file(path)
    output = []
    index = 0
    for record in records:
        for text in split_text(record['text'], chunk_size, overlap):
            output.append({
                'id': f'{source_id}:{index}',
                'text': text,
                'metadata': {
                    'source_id': source_id,
                    'file_name': path.name,
                    'file_type': path.suffix.lower().lstrip('.'),
                    'page': int(record['page'] or 0),
                    'chunk_index': index,
                },
            })
            index += 1
    return output
