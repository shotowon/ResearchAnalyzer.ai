from dataclasses import dataclass
from uuid import UUID


@dataclass
class UserAcct:
    id: int
    username: str
    email: str
    password: str
    is_activated: bool
    activation_id: UUID


@dataclass
class CreateBody:
    username: str
    email: str
    password: str
    activation_id: UUID


@dataclass
class CreateResult:
    id: int


@dataclass
class GetResult:
    id: int
    username: str
    activation_id: UUID
    is_activated: bool
    email: str
    password: str


@dataclass
class UpdateBody:
    id: int
    username: str | None
    email: str | None
    password: str | None
    is_activated: bool | None
    activation_id: UUID | None


@dataclass
class ActivateResult:
    user_id: int
