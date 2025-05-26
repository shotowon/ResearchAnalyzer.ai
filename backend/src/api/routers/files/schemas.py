from pydantic import BaseModel
from typing import List, Optional


class FileInfo(BaseModel):
    name: str
    id: int


class FileListResponse(BaseModel):
    files: List[FileInfo]


class IngestedFileInfo(BaseModel):
    id: int
    name: str
    document_id: str


class IngestedResponse(BaseModel):
    files: List[IngestedFileInfo]


class ProcessDOIRequest(BaseModel):
    doi: str


class ProcessResponse(BaseModel):
    message: str
    file_id: int
    ingested_id: int


class IngestResponse(BaseModel):
    message: str
    ingested_id: int


class ChatRequest(BaseModel):
    file_id: int
    prompt: str
    chat_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    source: str
    chat_id: str
    message_id: int


class SummarizeResponse(BaseModel):
    message: str
    summary: str
    summary_id: str


class SummaryResponse(BaseModel):
    summary: str
    summary_id: int


class MappingResponse(BaseModel):
    filename: str
    doc_id: str


class AllMappingsResponse(BaseModel):
    mappings: list[dict]
