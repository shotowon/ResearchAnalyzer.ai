from typing import Protocol

from .auth_token_models import (
    CreateBody,
    CreateResult,
    GetResult,
)


class AuthTokenStorage(Protocol):
    async def create(self, body: CreateBody) -> CreateResult: ...
    async def get_by_id(self, id: int) -> GetResult: ...
    async def get_by_token(self, token: str) -> GetResult: ...
    async def delete_token(self, token: str) -> None: ...
    async def token_exists(self, token: str) -> bool: ...


class ErrNotFound(Exception):
    pass


class ErrInternal(Exception):
    pass
