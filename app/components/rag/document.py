import os
from typing import List, Dict, Union
from io import BytesIO
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))


def extract_text_from_pdf(file_source: Union[str, bytes]) -> str:
    if isinstance(file_source, bytes):
        reader = PdfReader(BytesIO(file_source))
    else:
        reader = PdfReader(file_source)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text.strip()

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        # Find the end of the chunk
        end = start + chunk_size

        # If not at the end, try to break at a sentence or word boundary
        if end < text_length:
            # Try to find a sentence boundary (., !, ?)
            for sep in ['. ', '! ', '? ', '\n\n', '\n', ' ']:
                last_sep = text.rfind(sep, start, end)
                if last_sep != -1 and last_sep > start:
                    end = last_sep + len(sep)
                    break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start position with overlap
        start = end - overlap if end < text_length else text_length

    return chunks


def process_document(file_path: str) -> Dict:
    # Extract text from PDF
    text = extract_text_from_pdf(file_path)

    if not text:
        raise ValueError("Could not extract text from PDF. The file may be empty or image-based.")

    chunks = chunk_text(text)

    if not chunks:
        raise ValueError("No chunks created from the document.")

    return {
        "full_text": text,
        "chunks": chunks,
        "chunk_count": len(chunks),
        "total_characters": len(text)
    }