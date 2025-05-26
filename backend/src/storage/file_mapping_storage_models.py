from dataclasses import dataclass


@dataclass
class GetResult:
    id: int
    user_id: int
    filename: str
    content_type: str


@dataclass
class GetIngestedResult:
    id: int
    user_id: int
    mapping_id: int
    document_id: str


@dataclass
class CreateBody:
    user_id: int
    filename: str
    content_type: str


@dataclass
class CreateResult:
    id: int


@dataclass
class CreateIngestedBody:
    user_id: int
    mapping_id: int
    document_id: str


@dataclass
class CreateIngestedResult:
    id: int
