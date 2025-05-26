from typing import Protocol

from .file_mapping_storage_models import (
    GetResult,
    GetIngestedResult,
    CreateBody,
    CreateIngestedBody,
    CreateResult,
    CreateIngestedResult,
)


class MappingStorage(Protocol):
    async def list(
        self, user_id: int, limit: int = 15, offset: int = 0
    ) -> list[GetResult]: ...
    async def get(self, id: int) -> GetResult: ...
    async def create(self, body: CreateBody) -> CreateResult: ...
    async def list_ingested(
        self, user_id: int, limit: int = 15, offset: int = 0
    ) -> list[GetIngestedResult]: ...
    async def get_ingested(self, id: int) -> GetIngestedResult: ...
    async def create_ingested(
        self, body: CreateIngestedBody
    ) -> CreateIngestedResult: ...


class ErrNotFound(Exception):
    pass


class ErrInternal(Exception):
    pass
