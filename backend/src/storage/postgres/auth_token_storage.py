from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

from src.gears.db import DB
from ..auth_token_models import (
    CreateBody,
    CreateResult,
    GetResult,
)
from ..auth_token_storage import (
    ErrInternal,
    ErrNotFound,
)

from .models.auth_token import AuthToken


class AuthTokenStorage:
    def __init__(self, db: DB):
        self.__db: DB = db

    async def create(self, body: CreateBody) -> CreateResult:
        async with self.__db.session_maker() as session:
            new_token = AuthToken(token=body.token, user_id=body.user_id)
            session.add(new_token)
            try:
                await session.commit()
                await session.refresh(new_token)
                return CreateResult(int(new_token.id))
            except IntegrityError as e:
                raise ErrInternal(
                    "auth-token-storage: create: internal: integrity-error: {}".format(
                        str(e)
                    )
                )
            except Exception as e:
                raise ErrInternal(
                    "auth-token-storage: create: internal: {}".format(str(e))
                )

    async def get_by_id(self, id: int) -> GetResult:
        async with self.__db.session_maker() as session:
            stmt = select(AuthToken).where(AuthToken.id == id)
            result = await session.execute(stmt)
            auth_token = result.scalar_one_or_none()
            if auth_token is None:
                raise ErrNotFound(
                    "auth-token-storage: get_by_id: not-found: id = {}".format(id)
                )

            return GetResult(
                user_id=int(auth_token.user_id),
                token=str(auth_token.token),
            )

    async def get_by_token(self, token: str) -> GetResult:
        async with self.__db.session_maker() as session:
            try:
                stmt = select(AuthToken).where(AuthToken.token == token)
                result = await session.execute(stmt)
                auth_token = result.scalar_one_or_none()
            except Exception as e:
                raise ErrInternal(
                    "auth-token-storage: get_by_token: internal: {}".format(str(e))
                )

            if auth_token is None:
                raise ErrNotFound(
                    "auth-token-storage: get_by_token: not-found: token = {}".format(
                        token
                    )
                )

            return GetResult(
                user_id=int(auth_token.user_id),
                token=str(auth_token.token),
            )

    async def delete_token(self, token: str) -> None:
        async with self.__db.session_maker() as session:
            try:
                stmt = delete(AuthToken).where(AuthToken.token == token)

                result = await session.execute(stmt)
                session.commit()
            except Exception as e:
                raise ErrInternal(
                    "auth-token-storage: delete: internal: {}".format(str(e))
                )

            if result.rowcount == 0:
                raise ErrNotFound(
                    "auth-token-storage: delete: not-found: token = {}".format(token)
                )

    async def token_exists(self, token: str) -> bool:
        try:
            await self.get_by_token(token)
        except ErrNotFound:
            return False
        except Exception as e:
            raise ErrInternal(
                "auth-token-storage: token_exists: internal: {}".format(str(e))
            )

        return True
