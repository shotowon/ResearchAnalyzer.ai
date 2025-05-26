from typing import Protocol, Optional, List

from .message_storage_models import (
    GetResult,
    CreateBody,
    CreateResult,
    UpdateBody,
)


class MessageStorage(Protocol):
    async def create(self, body: CreateBody) -> CreateResult: ...
    async def get(self, id: str) -> GetResult: ...
    async def get_by_chat(self, chat_id: str) -> List[GetResult]: ...
    async def update(self, body: UpdateBody) -> Optional[GetResult]: ...
    async def delete(self, id: str) -> bool: ...


class ErrNotFound(Exception):
    pass


class ErrInternal(Exception):
    pass 