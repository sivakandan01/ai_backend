import os
import uuid
import aiofiles
from datetime import datetime
from fastapi import UploadFile, HTTPException
from app.components.rag.document import process_document
from app.components.rag.vectorstore import add_documents, search_documents, delete_document, get_user_documents
from app.components.rag.schema import DocumentResponse, QueryResponse, DeleteResponse, SourceChunk
from app.utils.prompt import get_rag_prompt
from app.utils.s3 import upload_file_to_s3, get_s3_url, delete_from_s3
from app.constants.files import S3_DOCUMENTS_PREFIX

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class RagService:
    def __init__(self, db, llm_service):
        self.db = db
        self.llm_service = llm_service

    async def upload_file(self, file: UploadFile, user_id: str) -> DocumentResponse:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Generate unique document ID
        document_id = str(uuid.uuid4())
        unique_filename = f"{document_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        try:
            # Save uploaded file
            contents = await file.read()
            file_size = len(contents)

            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(contents)

            # Process the document (extract text and chunk)
            processed_data = process_document(file_path)

            # Add to vector store
            chunks_added = add_documents(
                document_id=document_id,
                filename=file.filename,
                chunks=processed_data["chunks"],
                user_id=user_id
            )

            bucket = os.getenv('BUCKET_NAME')
            region = os.getenv('S3_REGION', 'ap-south-1')
            s3_key = f"{S3_DOCUMENTS_PREFIX}{unique_filename}"

            with open(file_path, 'rb') as f:
                s3_url = upload_file_to_s3(
                    file_obj=f,
                    bucket=bucket,
                    key=s3_key,
                    content_type='application/pdf'
                )

            if os.path.exists(file_path):
                os.remove(file_path)

            # Save metadata to MongoDB
            document_metadata = {
                "document_id": document_id,
                "user_id": user_id,
                "filename": file.filename,
                "file_size": file_size,
                "chunk_count": chunks_added,
                "upload_date": datetime.utcnow(),
                "status": "indexed",
                "s3_url": s3_url
            }
            await self.db.documents.insert_one(document_metadata)

            return DocumentResponse(
                success=True,
                document_id=document_id,
                filename=file.filename,
                chunks_created=chunks_added,
                message="Document uploaded and indexed successfully"
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

    async def query_documents(self, query: str, user_id: str, top_k: int = 5, document_ids: list = None) -> QueryResponse:
        try:
            # Search for relevant chunks
            search_results = search_documents(
                query=query,
                user_id=user_id,
                top_k=top_k,
                document_ids=document_ids
            )

            if not search_results:
                return QueryResponse(
                    answer="I don't have any relevant information to answer your question. Please upload some documents first.",
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

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error querying documents: {str(e)}")

    async def list_user_documents(self, user_id: str):
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
                    "chunk_count": doc["chunk_count"],
                    "upload_date": doc["upload_date"],
                    "status": doc["status"]
                })

            return {"documents": formatted_docs, "total": len(formatted_docs)}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

    async def delete_document(self, document_id: str, user_id: str) -> DeleteResponse:
        try:
            # Verify document belongs to user
            document = await self.db.documents.find_one({"document_id": document_id, "user_id": user_id})

            if not document:
                raise HTTPException(status_code=404, detail="Document not found or access denied")

            # Delete from vector store
            chunks_deleted = delete_document(document_id, user_id)

            # Delete from MongoDB
            await self.db.documents.delete_one({"document_id": document_id})

            if 's3_url' in document:
                bucket = os.getenv('BUCKET_NAME')
                unique_filename = f"{document_id}_{document['filename']}"
                s3_key = f"{S3_DOCUMENTS_PREFIX}{unique_filename}"
                delete_from_s3(bucket, s3_key)

            return DeleteResponse(
                success=True,
                message=f"Document deleted successfully. Removed {chunks_deleted} chunks.",
                document_id=document_id
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")