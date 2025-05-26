from dataclasses import dataclass
from datetime import datetime


@dataclass
class GetResult:
    id: str
    file_id: str
    title: str
    created_at: datetime
    updated_at: datetime


@dataclass
class CreateBody:
    file_id: str
    title: str


@dataclass
class CreateResult:
    id: str


@dataclass
class UpdateBody:
    id: str
    title: str 