from typing import Protocol, Optional

from .summary_storage_models import (
    GetResult,
    CreateBody,
    CreateResult,
    UpdateBody,
)


class SummaryStorage(Protocol):
    async def create(self, body: CreateBody) -> CreateResult: ...
    async def get(self, id: str) -> GetResult: ...
    async def get_by_file(self, file_id: str) -> Optional[GetResult]: ...
    async def update(self, body: UpdateBody) -> Optional[GetResult]: ...
    async def delete(self, id: str) -> bool: ...


class ErrNotFound(Exception):
    pass


class ErrInternal(Exception):
    pass 