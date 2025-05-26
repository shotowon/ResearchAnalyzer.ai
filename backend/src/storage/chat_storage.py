from typing import Protocol, Optional, List

from .chat_storage_models import (
    GetResult,
    CreateBody,
    CreateResult,
    UpdateBody,
)


class ChatStorage(Protocol):
    async def create(self, body: CreateBody) -> CreateResult: ...
    async def get(self, id: str) -> GetResult: ...
    async def get_by_file(self, file_id: str) -> List[GetResult]: ...
    async def update(self, body: UpdateBody) -> Optional[GetResult]: ...
    async def delete(self, id: str) -> bool: ...


class ErrNotFound(Exception):
    pass


class ErrInternal(Exception):
    pass 