from dataclasses import asdict

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete
from uuid import UUID

from src.gears.db import DB

from ..user_acct_models import (
    CreateBody,
    CreateResult,
    GetResult,
    UpdateBody,
    ActivateResult,
)

from ..user_acct_storage import (
    ErrInternal,
    ErrNotFound,
    ErrNothingToUpdate,
    ErrAlreadyActivated,
)

from .models.user_acct import UserAcct


class UserAcctStorage:
    def __init__(self, db: DB):
        self.db: DB = db

    async def create(self, body: CreateBody) -> CreateResult:
        try:
            async with self.db.session_maker() as session:
                new_user = UserAcct(
                    username=body.username,
                    email=body.email,
                    password=body.password,
                    activation_id=body.activation_id,
                )
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                return CreateResult(new_user.id)
        except IntegrityError as e:
            raise ErrInternal(
                "user-acct-storage: create: internal: integrity-error: {}".format(
                    str(e)
                )
            )
        except Exception as e:
            raise ErrInternal("user-acct-storage: create: internal: {}".format(str(e)))

    async def get_by_id(self, id: int) -> GetResult:
        try:
            async with self.db.session_maker() as session:
                stmt = select(UserAcct).where(UserAcct.id == id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
        except Exception as e:
            raise ErrInternal(
                "user-acct-storage: get_by_id: internal: {}".format(str(e))
            )

        try:
            user = result.scalar_one_or_none()
        except Exception as e:
            raise ErrInternal(
                "user-acct-storage: get_by_id: internal: {}".format(str(e))
            )

        if user is None:
            raise ErrNotFound(
                "user-acct-storage: get_by_id: not found: id = {}".format(id)
            )

        return GetResult(
            id=user.id,
            username=user.username,
            email=user.email,
            is_activated=user.is_activated,
            password=user.password,
        )

    async def get_by_username(self, username: str) -> GetResult:
        try:
            async with self.db.session_maker() as session:
                stmt = select(UserAcct).where(UserAcct.username == username)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
        except Exception as e:
            raise ErrInternal(
                "user-acct-storage: get_by_username: internal: {}".format(str(e))
            )

        try:
            user = result.scalar_one_or_none()
        except Exception as e:
            raise ErrInternal(
                "user-acct-storage: get_by_username: internal: {}".format(str(e))
            )

        if user is None:
            raise ErrNotFound(
                "user-acct-storage: get_by_username: not found: username = {}".format(
                    username
                )
            )
        return GetResult(
            id=user.id,
            username=user.username,
            email=user.email,
            is_activated=user.is_activated,
            password=user.password,
        )

    async def get_by_email(self, email: str) -> GetResult:
        try:
            async with self.db.session_maker() as session:
                stmt = select(UserAcct).where(UserAcct.email == email)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
        except Exception as e:
            raise ErrInternal(
                "user-acct-storage: get_by_email: internal: {}".format(str(e))
            )

        if user is None:
            raise ErrNotFound(
                "user-acct-storage: get_by_email: not found: email = {}".format(email)
            )
        try:
            get_result = GetResult(
                id=user.id,
                username=user.username,
                email=user.email,
                is_activated=user.is_activated,
                activation_id=user.activation_id,
                password=user.password,
            )
        except Exception as e:
            raise ErrInternal(
                "user-acct-storage: get_by_email: internal: {}".format(str(e))
            )
        return get_result

    async def username_exists(self, username: str) -> bool:
        try:
            async with self.db.session_maker() as session:
                stmt = select(UserAcct.username).where(UserAcct.username == username)
                result = await session.execute(stmt)
                return result.scalar_one_or_none() is not None
        except Exception as e:
            raise ErrInternal(
                "user-acct-storage: username_exists: internal: {}".format(str(e))
            )

    async def email_exists(self, email: str) -> bool:
        try:
            async with self.db.session_maker() as session:
                stmt = select(UserAcct).where(UserAcct.email == email)
                result = await session.execute(stmt)
                return result.scalar_one_or_none() is not None
        except Exception as e:
            raise ErrInternal(
                "user-acct-storage: email_exists: internal: {}".format(str(e))
            )

    async def delete_by_id(self, id: int) -> None:
        async with self.db.session_maker() as session:
            try:
                stmt = delete(UserAcct).where(UserAcct.id == id)
                result = await session.execute(stmt)
            except Exception as e:
                raise ErrInternal(
                    "user-acct-storage: delete_by_id: internal: {}".format(str(e))
                )

            if result.rowcount == 0:
                raise ErrNotFound(
                    "user-acct-storage: delete_by_id: not found: id = {}".format(id)
                )

            try:
                await session.commit()
            except Exception as e:
                raise ErrInternal(
                    "user-acct-storage: delete_by_id: internal: {}".format(str(e))
                )

    async def delete_by_username(self, username: str) -> None:
        async with self.db.session_maker() as session:
            try:
                stmt = delete(UserAcct).where(UserAcct.username == username)
                result = await session.execute(stmt)
            except Exception as e:
                raise ErrInternal(
                    "user-acct-storage: delete_by_username: internal: {}".format(str(e))
                )
            if result.rowcount == 0:
                raise ErrNotFound(
                    "user-acct-storage: delete_by_username: not found: username = {}".format(
                        username
                    )
                )
            try:
                await session.commit()
            except Exception as e:
                raise ErrInternal(
                    "user-acct-storage: delete_by_username: internal: {}".format(str(e))
                )

    async def update(self, body: UpdateBody) -> None:
        update_data = {k: v for k, v in asdict(body) if v is not None and k != "id"}
        if not update_data:
            raise ErrNothingToUpdate(
                "user-acct-storage: update: no data to update: update data = {}".format(
                    update_data
                )
            )

        async with self.db.session_maker() as session:
            try:
                stmt = (
                    update(UserAcct).where(UserAcct.id == body.id).values(**update_data)
                )
                result = await session.execute(stmt)
            except Exception as e:
                raise ErrInternal(
                    "user-acct-storage: update: internal: {}".format(str(e))
                )
            if result.rowcount == 0:
                raise ErrNotFound(
                    "user-acct-storage: update: not found: id = {}".format(body.id)
                )

            try:
                await session.commit()
            except Exception as e:
                raise ErrInternal(
                    "user-acct-storage: update: internal: {}".format(str(e))
                )

    async def activate(self, activation_id: UUID) -> None:
        async with self.db.session_maker() as session:
            try:
                stmt = select(UserAcct).where(UserAcct.activation_id == activation_id)

                result = await session.execute(statement=stmt)
                user = result.scalar_one_or_none()
            except Exception as e:
                raise ErrInternal(
                    "user-acct-storage: activate: internal: {}".format(str(e))
                )

            if user is None:
                raise ErrNotFound("user-acct-storage: activate: not found")

            if user.is_activated:
                raise ErrAlreadyActivated(
                    "user-acct-storage: activate: already-activated: {}".format(
                        str(activation_id)
                    )
                )

            try:
                stmt = (
                    update(UserAcct)
                    .where(UserAcct.activation_id == activation_id)
                    .values(is_activated=True)
                )

                result = await session.execute(statement=stmt)
                await session.commit()
                return ActivateResult(user_id=user.id)
            except Exception as e:
                raise ErrInternal(
                    "user-acct-storage: activate: internal: {}".format(str(e))
                )
