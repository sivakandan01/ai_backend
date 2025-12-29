from fastapi import APIRouter, UploadFile, File, Request, Depends
from app.components.rag.service import RagService
from app.components.rag.schema import QueryRequest, QueryResponse, DocumentResponse, DeleteResponse
from app.helpers.auth import check_for_auth
from app.helpers.dependencies import get_rag_service

router = APIRouter(prefix="/rag", tags=["rag"], dependencies=[Depends(check_for_auth)])

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    service: RagService = Depends(get_rag_service)
):
    user = request.state.user
    result = await service.upload_file(file, user["id"])
    return result

@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: Request,
    query_request: QueryRequest,
    service: RagService = Depends(get_rag_service)
):
    user = request.state.user
    result = await service.query_documents(
        query=query_request.query,
        user_id=user["id"],
        top_k=query_request.top_k,
        document_ids=query_request.document_ids
    )
    return result

@router.get("/documents")
async def list_documents(
    request: Request,
    service: RagService = Depends(get_rag_service)
):
    user = request.state.user
    result = await service.list_user_documents(user["id"])
    return result

@router.delete("/documents/{document_id}", response_model=DeleteResponse)
async def delete_document(
    request: Request,
    document_id: str,
    service: RagService = Depends(get_rag_service)
):
    user = request.state.user
    result = await service.delete_document(document_id, user["id"])
    return result