from dataclasses import dataclass
from datetime import datetime


@dataclass
class GetResult:
    id: str
    chat_id: str
    content: str
    role: str
    created_at: datetime
    updated_at: datetime


@dataclass
class CreateBody:
    chat_id: str
    content: str
    role: str


@dataclass
class CreateResult:
    id: str


@dataclass
class UpdateBody:
    id: str
    content: str 