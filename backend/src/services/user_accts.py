from dataclasses import dataclass

from src.storage.user_acct_storage import UserAcctStorage, ErrInternal
from src.storage.user_acct_models import CreateBody


@dataclass
class RegisterBody:
    username: str
    email: str
    password: str


@dataclass
class RegisterResult:
    id: int
    err: str


class ErrUsernameTaken(Exception):
    pass


class ErrEmailTaken(Exception):
    pass


class UserAcctService:
    def __init__(self, storage: UserAcctStorage):
        self.__storage = storage

    async def register(self, body: RegisterBody) -> RegisterResult:
        if await self.__storage.username_exists(body.username):
            raise ErrUsernameTaken
        if await self.__storage.email_exists(body.email):
            raise ErrEmailTaken

        try:
            result = await self.__storage.create(
                CreateBody(
                    username=body.username,
                    email=body.email,
                    password=body.password,
                )
            )
        except ErrInternal as e:
            raise e

        return RegisterResult(id=result.id)
