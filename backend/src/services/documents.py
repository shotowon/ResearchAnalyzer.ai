from dataclasses import dataclass
from io import BytesIO

from pgpt_python.client import AsyncPrivateGPTApi

from src.storage.file_mapping_storage import MappingStorage
from src.storage import (
    file_mapping_storage_models,
    file_storage_models,
    file_storage,
    file_mapping_storage,
    chat_storage,
    message_storage,
    summary_storage,
    chat_storage_models,
    message_storage_models,
    summary_storage_models,
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
    chat_id: str
    message_id: str


@dataclass
class SummarizeResult:
    summary: str
    summary_id: str


class ErrInternal(Exception):
    pass


class ErrNotFound(Exception):
    pass


class ErrEmptyPDF(Exception):
    pass


class DocumentService:
    def __init__(
        self,
        mapping_storage: MappingStorage,
        article_storage: ArticleStorage,
        gpt_api: AsyncPrivateGPTApi,
        chat_storage: chat_storage.ChatStorage,
        message_storage: message_storage.MessageStorage,
        summary_storage: summary_storage.SummaryStorage,
    ):
        self.article_storage = article_storage
        self.mapping_storage = mapping_storage
        self.api = gpt_api
        self.chat_storage = chat_storage
        self.message_storage = message_storage
        self.summary_storage = summary_storage

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
        except file_storage.ErrNotFound as e:
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
            print("eheh")
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

    async def chat(self, id: int, prompt: str, chat_id: str = None) -> ChatResult:
        try:
            ingested = await self.mapping_storage.get_ingested(id)
        except Exception as e:
            raise ErrInternal(
                f"document-service: chat: failed to get ingested doc with id = {id}: internal: {str(e)}"
            )

        try:
            response = await self.api.contextual_completions.prompt_completion(
                prompt=prompt,
                use_context=True,
                context_filter={"docs_ids": [ingested.document_id]},
                include_sources=True,
            )

            result = response.choices[0]

            # Create new chat if chat_id not provided
            if not chat_id:
                chat_result = await self.chat_storage.create(
                    chat_storage_models.CreateBody(
                        file_id=str(id),
                        title=prompt[:50] + "..."  # Use first 50 chars of prompt as title
                    )
                )
                chat_id = chat_result.id

            # Save user message
            await self.message_storage.create(
                message_storage_models.CreateBody(
                    chat_id=chat_id,
                    content=prompt,
                    role="user"
                )
            )

            # Save assistant message
            message_result = await self.message_storage.create(
                message_storage_models.CreateBody(
                    chat_id=chat_id,
                    content=result.message.content,
                    role="assistant"
                )
            )

        except Exception as e:
            raise ErrInternal(f"document-service: chat: failed to process chat: internal: {str(e)}")

        return ChatResult(
            response=result.message.content,
            source=result.sources[0].document.doc_metadata["file_name"],
            chat_id=chat_id,
            message_id=message_result.id
        )

    async def summarize(self, id: int) -> SummarizeResult:
        try:
            ingested = await self.mapping_storage.get_ingested(id)
        except Exception as e:
            raise ErrInternal(
                f"document-service: summarize: failed to get ingested doc with id = {id}: internal: {str(e)}"
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
                f"document-service: summarize: failed to extract text from pdf: internal: {str(e)}"
            )

        summaries = []
        try:
            for chunk in chunks:
                response = await self.api.contextual_completions.prompt_completion(
                    prompt=f"Summarize this document:\n{chunk}"
                )

                if response.choices[0].message is not None:
                    summaries.append(response.choices[0].message.content)

            final_summary = " ".join(summaries)

            # Save the summary
            summary_result = await self.summary_storage.create(
                summary_storage_models.CreateBody(
                    file_id=str(id),
                    content=final_summary
                )
            )

        except Exception as e:
            raise ErrInternal(f"document-service: summarize: failed to process summary: internal: {str(e)}")

        return SummarizeResult(summary=final_summary, summary_id=summary_result.id)

    async def __ingest(self, data: bytes) -> str:
        doc_id = (
            await self.api.ingestion.ingest_file(file=BytesIO(data), timeout=500)
            .data[0]
            .doc_id
        )

        return doc_id
