from dataclasses import dataclass


@dataclass
class CreateBody:
    user_id: int
    token: str


@dataclass
class CreateResult:
    id: int


@dataclass
class GetResult:
    user_id: int
    token: str
