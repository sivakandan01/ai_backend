from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DocumentUpload(BaseModel):
    filename: str
    content_type: str


class DocumentMetadata(BaseModel):
    id: str
    user_id: str
    filename: str
    file_size: int
    chunk_count: int
    upload_date: datetime
    status: str = "processing" 


class DocumentResponse(BaseModel):
    success: bool
    document_id: str
    filename: str
    chunks_created: int
    message: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]
    total: int


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: Optional[List[str]] = None  # Filter to specific documents


class SourceChunk(BaseModel):
    document_id: str
    filename: str
    chunk_text: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    query: str


class DeleteResponse(BaseModel):
    success: bool
    message: str
    document_id: str