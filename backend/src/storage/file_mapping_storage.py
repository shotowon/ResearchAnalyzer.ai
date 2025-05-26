from typing import Protocol, List
from dataclasses import dataclass

from .file_mapping_storage_models import (
    GetResult,
    GetIngestedResult,
    CreateBody,
    CreateIngestedBody,
    CreateResult,
    CreateIngestedResult,
)


@dataclass
class CreateIngestedResult:
    id: str
    filename: str


@dataclass
class GetIngestedResult:
    id: str
    filename: str


class MappingStorage(Protocol):
    async def list(
        self, user_id: int, limit: int = 15, offset: int = 0
    ) -> List[GetResult]: ...
    async def get(self, id: int) -> GetResult: ...
    async def create(self, body: CreateBody) -> CreateResult: ...
    async def list_ingested(
        self, user_id: int, limit: int = 15, offset: int = 0
    ) -> List[GetIngestedResult]: ...
    async def get_ingested(self, id: int) -> GetIngestedResult: ...
    async def create_ingested(self, body: CreateIngestedBody) -> CreateIngestedResult: ...
    async def get_all_ingested(
        self,
    ) -> List[GetIngestedResult]: ...
    async def get_ingested(
        self,
        filename: str,
    ) -> GetIngestedResult: ...


class ErrNotFound(Exception):
    pass


class ErrInternal(Exception):
    pass
