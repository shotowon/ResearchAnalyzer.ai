from dataclasses import dataclass


@dataclass
class UserAcct:
    id: int
    username: str
    email: str
    password: str
    is_activated: bool


@dataclass
class CreateBody:
    username: str
    email: str
    password: str


@dataclass
class CreateResult:
    id: int


@dataclass
class GetResult:
    id: int
    username: str
    is_activated: bool
    email: str
    password: str


@dataclass
class UpdateBody:
    id: int
    username: str
    email: str
    password: str


@dataclass
class DeleteBody:
    id: int | None
    username: str | None
