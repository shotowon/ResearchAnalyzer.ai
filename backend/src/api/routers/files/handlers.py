from typing import Annotated
from pathlib import Path

from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, status, Response
from fastapi.responses import JSONResponse

from src.api.clients.scihub import SciHubApi
from src.services.documents import DocumentService, UploadBody
from src.init import logger as rootLogger

from ..dependencies import get_document_service, get_current_user
from .schemas import (
    FileListResponse,
    ProcessDOIRequest,
    ProcessResponse,
    ChatRequest,
    ChatResponse,
    SummarizeResponse,
    SummaryResponse,
    IngestedResponse,
    IngestResponse,
)


router = APIRouter()


@router.get("/list", response_model=FileListResponse)
async def list_files(
    current_user: Annotated[dict, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    """List all uploaded files for the current user."""
    logger = rootLogger.getChild("files.list")
    try:
        mappings = await document_service.mapping_storage.list(user_id=current_user["id"])
        files = [{"name": m.filename, "id": m.id} for m in mappings]
        return FileListResponse(files=files)
    except Exception as e:
        logger.error(f"Failed to list files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ingested", response_model=IngestedResponse)
async def list_ingested_files(
    current_user: Annotated[dict, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    """List all ingested files for the current user."""
    logger = rootLogger.getChild("files.list")
    try:
        mappings = await document_service.mapping_storage.list_ingested(user_id=current_user["id"])
        files = [{
            "id": m.id,
            "name": m.filename,
            "document_id": m.document_id
        } for m in mappings]
        return IngestedResponse(files=files)
    except Exception as e:
        logger.error(f"Failed to list ingested files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/{file_id}")
async def get_file(
    file_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    """Download a specific file."""
    logger = rootLogger.getChild("files.get")
    try:
        result = await document_service.download(user_id=current_user["id"], id=file_id)
        return Response(
            content=result.contents,
            media_type="application/pdf"
        )
    except Exception as e:
        logger.error(f"Failed to get file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=ProcessResponse)
async def upload_file(
    file: UploadFile,
    current_user: Annotated[dict, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    """Upload a new file."""
    logger = rootLogger.getChild("files.upload")
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")

        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        contents = await file.read()
        result = await document_service.upload(
            UploadBody(
                user_id=current_user["id"],
                filename=file.filename,
                contents=contents,
                content_type=file.content_type,
            )
        )

        # Ingest the file
        ingest_result = await document_service.save_ingest(
            user_id=current_user["id"],
            id=result.id
        )

        return ProcessResponse(
            message="File uploaded and processed successfully",
            file_id=result.id,
            ingested_id=ingest_result.id
        )
    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-doi", response_model=ProcessResponse)
async def process_doi(
    body: ProcessDOIRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    """Process a DOI link and download the PDF."""
    logger = rootLogger.getChild("files.process-doi")
    try:
        if not body.doi:
            raise HTTPException(status_code=400, detail="No DOI provided")

        _, html_content = await SciHubApi.get_page(body.doi)
        if not html_content:
            raise HTTPException(status_code=500, detail="Empty response from Sci-Hub")

        soup = BeautifulSoup(html_content, "html.parser")
        embed_tag = soup.find("embed")
        if not embed_tag or "src" not in embed_tag.attrs:
            raise HTTPException(status_code=404, detail="PDF not found on Sci-Hub")

        pdf_url = embed_tag["src"]
        if pdf_url.startswith("//"):
            pdf_url = "https:" + pdf_url

        pdf_filename = pdf_url.split("/")[-1].split("#")[0]
        response, pdf_content = await SciHubApi.get_pdf(pdf_url)

        if not response or not pdf_content:
            raise HTTPException(status_code=500, detail="Failed to download PDF")

        # Upload to document service
        result = await document_service.upload(
            UploadBody(
                user_id=current_user["id"],
                filename=pdf_filename,
                contents=pdf_content.encode(),
                content_type="application/pdf",
            )
        )

        # Ingest the file
        ingest_result = await document_service.save_ingest(
            user_id=current_user["id"],
            id=result.id
        )
        print(ingest_result)

        return ProcessResponse(
            message="PDF downloaded and processed successfully",
            file_id=result.id,
            ingested_id=ingest_result.id
        )
    except Exception as e:
        logger.error(f"Failed to process DOI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize/{file_id}", response_model=SummarizeResponse)
async def summarize_file(
    file_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    """Generate a summary for a specific file."""
    logger = rootLogger.getChild("files.summarize")
    try:
        result = await document_service.summarize(id=file_id)
        return SummarizeResponse(
            message="Summarization completed successfully",
            summary=result.summary,
            summary_id=result.summary_id
        )
    except Exception as e:
        logger.error(f"Failed to summarize file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/{file_id}", response_model=SummaryResponse)
async def get_summary(
    file_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    """Get the summary for a specific file."""
    logger = rootLogger.getChild("files.summary")
    try:
        summary = await document_service.summary_storage.get_by_file_id(file_id=str(file_id))
        return SummaryResponse(
            summary=summary.content,
            summary_id=summary.id
        )
    except Exception as e:
        logger.error(f"Failed to get summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat-with-doc", response_model=ChatResponse)
async def chat_with_document(
    request: ChatRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    """Chat with a specific document."""
    logger = rootLogger.getChild("files.chat")
    try:
        result = await document_service.chat(
            id=request.file_id,
            prompt=request.prompt,
            chat_id=request.chat_id
        )
        return ChatResponse(
            response=result.response,
            source=result.source,
            chat_id=result.chat_id,
            message_id=result.message_id
        )
    except Exception as e:
        logger.error(f"Failed to chat with document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/{file_id}", response_model=IngestResponse)
async def ingest_file(
    file_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    """Ingest a specific file."""
    logger = rootLogger.getChild("files.ingest")
    try:
        ingest_result = await document_service.save_ingest(
            user_id=current_user["id"],
            id=file_id
        )
        return IngestResponse(
            message="File ingested successfully",
            ingested_id=ingest_result.id
        )
    except Exception as e:
        logger.error(f"Failed to ingest file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
