import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
from app.core.chromadb import documents_collection
from fastapi import HTTPException

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")


def get_embedding(text: str) -> List[float]:
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": EMBEDDING_MODEL,
                "prompt": text
            }
        )
        response.raise_for_status()
        return response.json()["embedding"]

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Ollama. Make sure Ollama is running and '{EMBEDDING_MODEL}' model is pulled (ollama pull {EMBEDDING_MODEL})"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating embedding: {str(e)}"
        )


def add_documents(
    document_id: str,
    filename: str,
    chunks: List[str],
    user_id: str
) -> int:
    # Generate unique IDs for each chunk
    chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]

    # Generate embeddings for all chunks
    embeddings = [get_embedding(chunk) for chunk in chunks]

    # Create metadata for each chunk
    metadatas = [
        {
            "document_id": document_id,
            "filename": filename,
            "user_id": user_id,
            "chunk_index": i
        }
        for i in range(len(chunks))
    ]

    # Add to ChromaDB
    documents_collection.add(
        ids=chunk_ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas
    )

    return len(chunks)


def search_documents(
    query: str,
    user_id: str,
    top_k: int = 5,
    document_ids: Optional[List[str]] = None
) -> List[Dict]:
    # Generate embedding for the query
    query_embedding = get_embedding(query)

    # Build where filter for user_id and optional document_ids
    where_filter = {"user_id": user_id}

    if document_ids:
        where_filter["document_id"] = {"$in": document_ids}

    # Search in ChromaDB
    results = documents_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter
    )

    # Format results
    formatted_results = []
    if results['ids'] and len(results['ids']) > 0:
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                "chunk_id": results['ids'][0][i],
                "chunk_text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "score": results['distances'][0][i] if results['distances'] else 0.0
            })

    return formatted_results


def delete_document(document_id: str, user_id: str) -> int:
    # Get all chunks for this document and user
    results = documents_collection.get(
        where={
            "document_id": document_id,
            "user_id": user_id
        }
    )

    if not results['ids']:
        return 0

    # Delete all chunks
    documents_collection.delete(
        ids=results['ids']
    )

    return len(results['ids'])


def get_user_documents(user_id: str) -> List[Dict]:
    # Get all chunks for the user
    results = documents_collection.get(
        where={"user_id": user_id}
    )

    if not results['metadatas']:
        return []

    # Extract unique documents
    unique_docs = {}
    for metadata in results['metadatas']:
        doc_id = metadata['document_id']
        if doc_id not in unique_docs:
            unique_docs[doc_id] = {
                "document_id": doc_id,
                "filename": metadata['filename'],
                "chunk_count": 1
            }
        else:
            unique_docs[doc_id]['chunk_count'] += 1

    return list(unique_docs.values())