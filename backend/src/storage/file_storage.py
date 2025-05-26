from typing import Protocol

from .file_storage_models import DownloadResult, UploadBody


class ArticleStorage(Protocol):
    async def download_file(self, user_id: int, id: int) -> DownloadResult: ...
    async def upload(self, body: UploadBody) -> None: ...


class ErrInternal(Exception):
    pass


class ErrNotFound(Exception):
    pass
