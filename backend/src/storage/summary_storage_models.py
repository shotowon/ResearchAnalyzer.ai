from dataclasses import dataclass
from datetime import datetime


@dataclass
class GetResult:
    id: str
    file_id: str
    content: str
    created_at: datetime
    updated_at: datetime


@dataclass
class CreateBody:
    file_id: str
    content: str


@dataclass
class CreateResult:
    id: str


@dataclass
class UpdateBody:
    id: str
    content: str 