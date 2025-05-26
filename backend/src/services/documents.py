from dataclasses import dataclass
from io import BytesIO

from pgpt_python.client import AsyncPrivateGPTApi

from src.storage.file_mapping_storage import MappingStorage
from src.storage import (
    file_mapping_storage_models,
    file_storage_models,
    file_storage,
    file_mapping_storage,
)
from src.storage.file_storage import ArticleStorage
from src.gears import pdf, strings


@dataclass
class UploadBody:
    user_id: int
    filename: str
    contents: bytes
    content_type: str


@dataclass
class UploadResult:
    id: int


@dataclass
class IngestResult:
    id: int


@dataclass
class DownloadResult:
    contents: bytes


@dataclass
class ChatResult:
    response: str
    source: str


@dataclass
class SummarizeResult:
    summary: str


class ErrInternal(Exception):
    pass


class ErrEmptyPDF(Exception):
    pass


class ErrNotFound(Exception):
    pass


class DocumentService:
    def __init__(
        self,
        mapping_storage: MappingStorage,
        article_storage: ArticleStorage,
        gpt_api: AsyncPrivateGPTApi,
    ):
        self.article_storage = article_storage
        self.mapping_storage = mapping_storage
        self.api = gpt_api

    async def upload(self, body: UploadBody) -> UploadResult:
        try:
            upload_map_result = await self.mapping_storage.create(
                body=file_mapping_storage_models.CreateBody(
                    user_id=body.user_id,
                    filename=body.filename,
                    content_type=body.content_type,
                )
            )

            await self.article_storage.upload(
                file_storage_models.UploadBody(
                    user_id=body.user_id,
                    id=upload_map_result.id,
                    contents=body.contents,
                )
            )
        except Exception as e:
            raise ErrInternal("document-service: upload: internal: {}".format(str(e)))

        return UploadResult(id=upload_map_result.id)

    async def download(self, user_id: int, id: int) -> DownloadResult:
        try:
            result = await self.article_storage.download_file(user_id=user_id, id=id)
        except file_storage.ErrNotFound:
            raise ErrNotFound(
                "document-service: download: not-found: {}".format(str(e))
            )
        except Exception as e:
            raise ErrInternal("document-service: download: internal: {}".format(str(e)))

        return DownloadResult(contents=result.contents)

    async def save_ingest(self, user_id: int, id: int) -> IngestResult:
        try:
            result = await self.article_storage.download_file(user_id=user_id, id=id)
        except file_storage.ErrNotFound:
            raise ErrNotFound(
                "document-service: save_ingest: failed to download article: not-found: {}".format(
                    str(e)
                )
            )
        except Exception as e:
            raise ErrInternal(
                "document-service: save_ingest: failed to download article: internal: {}".format(
                    str(e)
                )
            )

        try:
            doc_id = await self.__ingest(result.contents)
        except Exception as e:
            raise ErrInternal(
                "document-service: save_ingest: failed to ingest article: internal: {}".format(
                    str(e)
                )
            )

        try:
            ingested_result = await self.mapping_storage.create_ingested(
                file_mapping_storage_models.CreateIngestedBody(
                    user_id=user_id,
                    mapping_id=id,
                    document_id=doc_id,
                )
            )
        except Exception as e:
            raise ErrInternal(
                "document-service: save_ingest: failed to create ingestion mapping: doc_id ={}, user_id ={}, mapping_id = {}: internal: {}".format(
                    doc_id,
                    user_id,
                    id,
                    str(e),
                )
            )

        return IngestResult(id=ingested_result.id)

    async def chat(self, id: int, prompt: str) -> ChatResult:
        try:
            ingested = await self.mapping_storage.get_ingested(id)
        except Exception as e:
            raise ErrInternal(
                "document-service: save_ingest: failed to get ingested doc with id = {}: internal: {}".format(
                    id,
                    str(e),
                )
            )
        try:
            response = await self.api.contextual_completions.prompt_completion(
                prompt=prompt,
                use_context=True,
                context_filter={"docs_ids": [ingested.document_id]},
                include_sources=True,
            )

            result = response.choices[0]

        except Exception as e:
            raise ErrInternal(
                "document-service: chat: failed to get ingested doc with id = {}: internal: {}".format(
                    id,
                    str(e),
                )
            )
        return ChatResult(
            response=result.message.content,
            source=result.sources[0].document.doc_metadata["file_name"],
        )

    async def summarize(self, id: int) -> SummarizeResult:
        try:
            ingested = await self.mapping_storage.get_ingested(id)
        except Exception as e:
            raise ErrInternal(
                "document-service: summarize: failed to get ingested doc with id = {}: internal: {}".format(
                    id,
                    str(e),
                )
            )
        downloaded = await self.article_storage.download_file(
            user_id=ingested.user_id, id=ingested.id
        )

        try:
            text = pdf.extract_text(pdf_contents=downloaded.contents)
            if not text.strip():
                raise ErrEmptyPDF("document-service: summarize: no contents in pdf")

            chunks = strings.split_text_into_chunks(text=text)
        except Exception as e:
            raise ErrInternal(
                "document-service: summarize: failed to extract text from pdf: internal: {}".format(
                    str(e)
                )
            )

        summaries = []
        try:
            for chunk in chunks:
                response = await self.api.contextual_completions.prompt_completion(
                    prompt=f"Summarize this document:\n{chunk}"
                )

                if response.choices[0].message is not None:
                    summaries.append(response.choices[0].message.content)
        except Exception as e:
            raise ErrInternal(f"An error occurred during summarization. {str(e)}")
        return SummarizeResult(summary=" ".join(summaries))

    async def __ingest(self, data: bytes) -> str:
        doc_id = (
            await self.__api.ingestion.ingest_file(file=BytesIO(data), timeout=500)
            .data[0]
            .doc_id
        )

        return doc_id
