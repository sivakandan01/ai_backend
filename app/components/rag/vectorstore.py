import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
from app.core.pinecone_client import index as pinecone_index
from fastapi import HTTPException

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def get_embedding(text: str) -> List[float]:
    try:
        if not HUGGINGFACE_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="HUGGINGFACE_API_KEY not configured in environment"
            )

        response = requests.post(
            f"https://api-inference.huggingface.co/models/{EMBEDDING_MODEL}",
            headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
            json={"inputs": text}
        )
        response.raise_for_status()

        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        elif isinstance(result, dict) and "embeddings" in result:
            return result["embeddings"]
        else:
            return result

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to HuggingFace API. Please check your internet connection."
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

    # Create vectors for Pinecone in the format (id, embedding, metadata)
    vectors = []
    for i, (chunk_id, embedding, chunk) in enumerate(zip(chunk_ids, embeddings, chunks)):
        vectors.append({
            "id": chunk_id,
            "values": embedding,
            "metadata": {
                "document_id": document_id,
                "filename": filename,
                "user_id": user_id,
                "chunk_index": i,
                "text": chunk  # Store the actual text in metadata
            }
        })

    # Upsert to Pinecone
    pinecone_index.upsert(vectors=vectors)

    return len(chunks)


def search_documents(
    query: str,
    user_id: str,
    top_k: int = 5,
    document_ids: Optional[List[str]] = None
) -> List[Dict]:
    # Generate embedding for the query
    query_embedding = get_embedding(query)

    # Build filter for user_id and optional document_ids
    filter_dict = {"user_id": {"$eq": user_id}}

    if document_ids:
        filter_dict["document_id"] = {"$in": document_ids}

    # Search in Pinecone
    results = pinecone_index.query(
        vector=query_embedding,
        top_k=top_k,
        filter=filter_dict,
        include_metadata=True
    )

    # Format results
    formatted_results = []
    for match in results.matches:
        formatted_results.append({
            "chunk_id": match.id,
            "chunk_text": match.metadata.get("text", ""),
            "metadata": {
                "document_id": match.metadata.get("document_id"),
                "filename": match.metadata.get("filename"),
                "user_id": match.metadata.get("user_id"),
                "chunk_index": match.metadata.get("chunk_index")
            },
            "score": match.score
        })

    return formatted_results


def delete_document(document_id: str, user_id: str) -> int:
    # Query to find all chunks for this document and user
    filter_dict = {
        "document_id": {"$eq": document_id},
        "user_id": {"$eq": user_id}
    }

    # Get all matching vectors
    results = pinecone_index.query(
        vector=[0] * 384,  # Dummy vector for metadata-only query
        top_k=10000,  # Large number to get all chunks
        filter=filter_dict,
        include_metadata=True
    )

    if not results.matches:
        return 0

    # Extract IDs and delete
    ids_to_delete = [match.id for match in results.matches]
    pinecone_index.delete(ids=ids_to_delete)

    return len(ids_to_delete)


def get_user_documents(user_id: str) -> List[Dict]:
    # Query to find all chunks for the user
    filter_dict = {"user_id": {"$eq": user_id}}

    # Get all matching vectors
    results = pinecone_index.query(
        vector=[0] * 384,  # Dummy vector for metadata-only query
        top_k=10000,  # Large number to get all chunks
        filter=filter_dict,
        include_metadata=True
    )

    if not results.matches:
        return []

    # Extract unique documents
    unique_docs = {}
    for match in results.matches:
        doc_id = match.metadata.get('document_id')
        if doc_id and doc_id not in unique_docs:
            unique_docs[doc_id] = {
                "document_id": doc_id,
                "filename": match.metadata.get('filename'),
                "chunk_count": 1
            }
        elif doc_id:
            unique_docs[doc_id]['chunk_count'] += 1

    return list(unique_docs.values())