from typing import Protocol

from .user_acct_models import (
    CreateBody,
    CreateResult,
    GetResult,
    UpdateBody,
    DeleteBody,
)


class UserAcctStorage(Protocol):
    async def create(self, req: CreateBody) -> CreateResult: ...
    async def username_exists(self, username: str) -> bool: ...
    async def email_exists(self, email: str) -> bool: ...
    async def get_by_id(self, id: int) -> GetResult: ...
    async def get_by_username(self, username: str) -> GetResult: ...
    async def update(self, req: UpdateBody) -> None: ...
    async def delete(self, req: DeleteBody) -> None: ...


class ErrNotFound(Exception):
    pass


class ErrInternal(Exception):
    pass
