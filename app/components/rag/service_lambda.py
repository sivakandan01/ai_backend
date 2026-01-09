import os
import uuid
import aiofiles
from datetime import datetime
from fastapi import UploadFile, HTTPException
from app.components.rag.schema import DocumentResponse, QueryResponse, DeleteResponse, SourceChunk
from app.utils.prompt import get_rag_prompt
from app.utils.s3 import upload_file_to_s3, get_s3_url, delete_from_s3
from app.constants.files import S3_DOCUMENTS_PREFIX
from app.components.rag.vectorstore import search_documents, delete_document

# Temporary directory (only for file upload buffer)
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class RagService:
    """
    RAG Service with Lambda integration

    This version uploads PDFs to S3 and lets Lambda process them asynchronously.
    Processing flow:
    1. User uploads PDF → FastAPI saves to S3
    2. S3 event triggers Lambda
    3. Lambda processes PDF (extract, chunk, embed, index)
    4. Lambda updates MongoDB status
    """

    def __init__(self, db, llm_service):
        self.db = db
        self.llm_service = llm_service

    async def upload_file(self, file: UploadFile, user_id: str) -> DocumentResponse:
        """
        Upload PDF to S3 and return immediately.
        Lambda will process the document asynchronously.
        """
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Generate unique document ID
        document_id = str(uuid.uuid4())
        unique_filename = f"{document_id}_{file.filename}"

        # Temporary file path for upload buffer
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        try:
            # Read uploaded file
            contents = await file.read()
            file_size = len(contents)

            # Validate file size (optional: max 10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            if file_size > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size is {max_size / (1024*1024):.0f}MB"
                )

            if file_size == 0:
                raise HTTPException(status_code=400, detail="File is empty")

            # Save temporarily for S3 upload
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(contents)

            # Upload to S3 (this triggers Lambda automatically)
            bucket = os.getenv('BUCKET_NAME')
            region = os.getenv('S3_REGION', 'ap-south-1')
            s3_key = f"{S3_DOCUMENTS_PREFIX}{unique_filename}"

            print(f"Uploading to S3: {bucket}/{s3_key}")

            with open(file_path, 'rb') as f:
                s3_url = upload_file_to_s3(
                    file_obj=f,
                    bucket=bucket,
                    key=s3_key,
                    content_type='application/pdf'
                )

            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)

            print(f"Document uploaded to S3: {s3_url}")

            # Save metadata to MongoDB with "processing" status
            document_metadata = {
                "document_id": document_id,
                "user_id": user_id,
                "filename": file.filename,
                "file_size": file_size,
                "chunk_count": 0,  # Will be updated by Lambda
                "upload_date": datetime.utcnow(),
                "status": "processing",  # Lambda will update to "indexed" or "error"
                "s3_url": s3_url
            }
            await self.db.documents.insert_one(document_metadata)

            print(f"Document metadata saved to MongoDB: {document_id}")

            # Return immediately (Lambda is processing in background)
            return DocumentResponse(
                success=True,
                document_id=document_id,
                filename=file.filename,
                chunks_created=0,  # Not yet processed
                message="Document uploaded successfully. Processing in background..."
            )

        except HTTPException:
            # Clean up temp file
            if os.path.exists(file_path):
                os.remove(file_path)
            raise
        except Exception as e:
            # Clean up temp file
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

    async def get_document_status(self, document_id: str, user_id: str):
        """
        Check the processing status of a document

        Status values:
        - "processing": Lambda is currently processing
        - "indexed": Document is ready for querying
        - "error": Processing failed
        """
        try:
            document = await self.db.documents.find_one({
                "document_id": document_id,
                "user_id": user_id
            })

            if not document:
                raise HTTPException(status_code=404, detail="Document not found")

            return {
                "document_id": document_id,
                "filename": document["filename"],
                "status": document["status"],
                "chunk_count": document.get("chunk_count", 0),
                "upload_date": document["upload_date"],
                "processed_at": document.get("processed_at"),
                "error_message": document.get("error_message")
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching document status: {str(e)}")

    async def query_documents(self, query: str, user_id: str, top_k: int = 5, document_ids: list = None) -> QueryResponse:
        """
        Query documents using RAG

        Note: Only queries documents with status="indexed"
        """
        try:
            # Check if user has any indexed documents
            if document_ids:
                # Verify all requested documents are indexed
                for doc_id in document_ids:
                    doc = await self.db.documents.find_one({
                        "document_id": doc_id,
                        "user_id": user_id
                    })
                    if not doc:
                        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
                    if doc["status"] != "indexed":
                        raise HTTPException(
                            status_code=400,
                            detail=f"Document {doc_id} is still processing. Status: {doc['status']}"
                        )

            # Search for relevant chunks
            search_results = search_documents(
                query=query,
                user_id=user_id,
                top_k=top_k,
                document_ids=document_ids
            )

            if not search_results:
                return QueryResponse(
                    answer="I don't have any relevant information to answer your question. Please upload some documents first or wait for documents to finish processing.",
                    sources=[],
                    query=query
                )

            # Prepare context from retrieved chunks
            context = "\n\n".join([
                f"[Source {i+1} from {result['metadata']['filename']}]:\n{result['chunk_text']}"
                for i, result in enumerate(search_results)
            ])

            # Generate answer using LLM with context
            prompt = get_rag_prompt(query, context)
            answer = await self.llm_service.generate_llm_text(prompt)

            # Format sources
            sources = [
                SourceChunk(
                    document_id=result['metadata']['document_id'],
                    filename=result['metadata']['filename'],
                    chunk_text=result['chunk_text'],
                    score=float(result['score'])
                )
                for result in search_results
            ]

            return QueryResponse(
                answer=answer,
                sources=sources,
                query=query
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error querying documents: {str(e)}")

    async def list_user_documents(self, user_id: str):
        """
        List all documents for a user with their processing status
        """
        try:
            documents = await self.db.documents.find({"user_id": user_id}).to_list(length=None)

            # Format response
            formatted_docs = []
            for doc in documents:
                formatted_docs.append({
                    "id": str(doc["_id"]),
                    "document_id": doc["document_id"],
                    "filename": doc["filename"],
                    "file_size": doc["file_size"],
                    "chunk_count": doc.get("chunk_count", 0),
                    "upload_date": doc["upload_date"],
                    "status": doc["status"],
                    "error_message": doc.get("error_message"),
                    "processed_at": doc.get("processed_at")
                })

            # Group by status for summary
            status_counts = {
                "processing": len([d for d in formatted_docs if d["status"] == "processing"]),
                "indexed": len([d for d in formatted_docs if d["status"] == "indexed"]),
                "error": len([d for d in formatted_docs if d["status"] == "error"])
            }

            return {
                "documents": formatted_docs,
                "total": len(formatted_docs),
                "status_summary": status_counts
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

    async def delete_document(self, document_id: str, user_id: str) -> DeleteResponse:
        """
        Delete document from vector store, MongoDB, and S3
        """
        try:
            # Verify document belongs to user
            document = await self.db.documents.find_one({"document_id": document_id, "user_id": user_id})

            if not document:
                raise HTTPException(status_code=404, detail="Document not found or access denied")

            # Delete from vector store (only if status is indexed)
            chunks_deleted = 0
            if document["status"] == "indexed":
                try:
                    chunks_deleted = delete_document(document_id, user_id)
                except Exception as e:
                    print(f"Warning: Failed to delete from vector store: {str(e)}")

            # Delete from MongoDB
            await self.db.documents.delete_one({"document_id": document_id})

            # Delete from S3
            if 's3_url' in document:
                try:
                    bucket = os.getenv('BUCKET_NAME')
                    unique_filename = f"{document_id}_{document['filename']}"
                    s3_key = f"{S3_DOCUMENTS_PREFIX}{unique_filename}"
                    delete_from_s3(bucket, s3_key)
                except Exception as e:
                    print(f"Warning: Failed to delete from S3: {str(e)}")

            return DeleteResponse(
                success=True,
                message=f"Document deleted successfully. Removed {chunks_deleted} chunks.",
                document_id=document_id
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")
