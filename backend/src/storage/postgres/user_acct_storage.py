from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from src.gears.db import DB

from ..user_acct_models import (
    CreateBody,
    CreateResult,
    GetOneBody,
    GetResult,
    UpdateBody,
    DeleteBody,
)

from ..user_acct_storage import (
    ErrInternal,
)

from .models.user_acct import UserAcct


class UserAcctStorage:
    def __init__(self, db: DB):
        self.db: DB = db

    async def create(self, req: CreateBody) -> CreateResult:
        async with self.db.session_maker() as session:
            new_user = UserAcct(
                username=req.username,
                email=req.email,
                password=req.password,
            )
            session.add(new_user)
            try:
                await session.commit()
                await session.refresh(new_user)
                return CreateResult(new_user.id)
            except IntegrityError as e:
                raise ErrInternal("internal: integrity-error: {}".format(str(e)))
            except Exception as e:
                raise ErrInternal("internal: {}".format(str(e)))

    async def get_one(self, req: GetOneBody) -> GetResult:
        return GetResult(0, "", False, "", "")

    async def username_exists(self, username: str) -> bool:
        async with self.db.session_maker() as session:
            stmt = select(UserAcct).where(UserAcct.username == username)
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

    async def email_exists(self, email: str) -> bool:
        async with self.db.session_maker() as session:
            stmt = select(UserAcct).where(UserAcct.email == email)
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

    async def update(self, req: UpdateBody) -> None:
        return None

    async def delete(self, req: DeleteBody) -> None:
        return None
