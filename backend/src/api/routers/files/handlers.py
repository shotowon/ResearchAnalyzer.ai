from typing import Annotated
from pathlib import Path

from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, File, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse

from src.api.clients.scihub import SciHubApi
from src.consts import DOWNLOAD_FOLDER
from src.services.documents import DocumentService, UploadBody
from src.services.pdf import download_pdf
from src.init import logger as rootLogger
from src.crud.temp_cruds import get_mapping, get_all_ingested

from ..dependencies import get_document_service
from .schemas import (
    FileListResponse,
    ProcessDOIRequest,
    ProcessResponse,
    ChatRequest,
    ChatResponse,
    SummarizeResponse,
    SummaryResponse,
    MappingResponse,
    AllMappingsResponse,
    IngestedResponse,
)


router = APIRouter()


@router.get("/list", response_model=FileListResponse)
async def list_files():
    try:
        files = [
            {"name": file.name, "path": str(file.resolve())}
            for file in DOWNLOAD_FOLDER.iterdir()
            if file.is_file() and file.suffix == ".pdf"
        ]
        return FileListResponse(files=files, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")


@router.get("/{file_name}")
async def get_file(file_name: str):
    file_path = DOWNLOAD_FOLDER / file_name
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")


@router.get("/summarize/{file_name}", response_model=SummarizeResponse)
async def summarize_pdf(
    file_name: str,
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    logger = rootLogger.getChild("files.summarize")
    try:
        file_path = DOWNLOAD_FOLDER / file_name
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        file_id = get_mapping(file_name)
        if not file_id:
            raise HTTPException(
                status_code=404, detail="Document ID not found for the given file"
            )

        result = await document_service.summarize(int(file_id))

        return SummarizeResponse(
            message="Summarization completed",
            status_code=200,
            summary=result.summary,
            summary_id=result.summary_id,
        )
    except Exception as e:
        logger.error(f"Failed to summarize file: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Failed to summarize file"},
        )


@router.post("/process-doi", response_model=ProcessResponse)
async def process_doi(
    body: ProcessDOIRequest,
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    logger = rootLogger.getChild("files.process-doi")
    try:
        if not body.doi:
            raise HTTPException(status_code=400, detail="Provide a DOI")

        _, html_content = await SciHubApi.get_page(body.doi)
        if not html_content:
            raise HTTPException(status_code=500, detail="Empty response content")

        soup = BeautifulSoup(html_content, "html.parser")
        embed_tag = soup.find("embed")
        if embed_tag and "src" in embed_tag.attrs:
            pdf_url = embed_tag["src"]

            if pdf_url.startswith("//"):
                pdf_url = "https:" + pdf_url

            pdf_filename = pdf_url.split("/")[-1].split("#")[0]
            file_path = await download_pdf(pdf_url, pdf_filename)

            if file_path:
                # Read the file contents
                with open(file_path, "rb") as f:
                    contents = f.read()

                # Upload to document service
                result = await document_service.upload(
                    UploadBody(
                        user_id=1,  # TODO: Get from auth
                        filename=pdf_filename,
                        contents=contents,
                        content_type="application/pdf",
                    )
                )

                # Ingest the file
                await document_service.save_ingest(user_id=1, id=result.id)

                return ProcessResponse(
                    message="PDF downloaded and processed successfully",
                    file_path=str(file_path),
                )

        raise HTTPException(
            status_code=404, detail="PDF download URL not found in the page content"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to process DOI: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/upload", response_model=ProcessResponse)
async def upload_pdf(
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    file: UploadFile = File(None),
):
    logger = rootLogger.getChild("files.upload")
    try:
        if not file:
            raise HTTPException(status_code=400, detail="Provide a file")

        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Uploaded file must be a PDF")

        if file.filename is None:
            raise HTTPException(status_code=400, detail="Empty filename")

        contents = await file.read()
        result = await document_service.upload(
            UploadBody(
                user_id=1,  # TODO: Get from auth
                filename=file.filename,
                contents=contents,
                content_type=file.content_type,
            )
        )

        # Save locally for compatibility
        file_path = DOWNLOAD_FOLDER / file.filename
        with open(file_path, "wb") as f:
            f.write(contents)

        # Ingest the file
        await document_service.save_ingest(user_id=1, id=result.id)

        return ProcessResponse(
            message="PDF uploaded and processed successfully",
            file_path=str(file_path),
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to upload PDF: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/chat", response_model=ChatResponse)
async def chat_with_doc(
    request: ChatRequest,
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    logger = rootLogger.getChild("files.chat")
    try:
        file_id = get_mapping(request.filename)
        if not file_id:
            raise HTTPException(
                status_code=404, detail="Document ID not found for the given file"
            )

        result = await document_service.chat(
            id=int(file_id), prompt=request.prompt, chat_id=request.chat_id
        )
        return ChatResponse(
            response=result.response,
            source=result.source,
            chat_id=result.chat_id,
            message_id=result.message_id,
        )
    except Exception as e:
        logger.error(f"Failed to chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during chat: {str(e)}")


@router.get("/mapping/{filename}", response_model=MappingResponse)
async def get_file_mapping(
    filename: str,
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    """Fetch the GPT document ID for a given file."""
    doc_id = get_mapping(filename)
    if not doc_id:
        raise HTTPException(
            status_code=404, detail="Document ID not found for the given file"
        )
    return MappingResponse(filename=filename, doc_id=doc_id)


@router.get("/mappings", response_model=AllMappingsResponse)
async def get_all_mappings(
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    """Fetch all the GPT document IDs mapped to filenames."""
    return AllMappingsResponse(mappings=get_all_ingested())


@router.get("/ingested", response_model=IngestedResponse)
async def get_all_ingested(
    document_service: Annotated[DocumentService, Depends(get_document_service)],
):
    data = document_service.api.ingestion.list_ingested().data
    return IngestedResponse(data=data)
