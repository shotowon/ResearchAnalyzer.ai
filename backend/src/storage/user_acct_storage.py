from typing import Protocol

from uuid import UUID

from .user_acct_models import (
    CreateBody,
    CreateResult,
    GetResult,
    UpdateBody,
    ActivateResult,
)


class UserAcctStorage(Protocol):
    async def create(self, body: CreateBody) -> CreateResult: ...
    async def username_exists(self, username: str) -> bool: ...
    async def email_exists(self, email: str) -> bool: ...
    async def get_by_id(self, id: int) -> GetResult: ...
    async def get_by_username(self, username: str) -> GetResult: ...
    async def get_by_email(self, email: str) -> GetResult: ...
    async def delete_by_id(self, id: int) -> None: ...
    async def delete_by_username(self, username: str) -> None: ...
    async def update(self, body: UpdateBody) -> None: ...
    async def activate(self, activation_id: UUID) -> ActivateResult: ...


class ErrNotFound(Exception):
    pass


class ErrNothingToUpdate(Exception):
    pass


class ErrAlreadyActivated(Exception):
    pass


class ErrInternal(Exception):
    pass
