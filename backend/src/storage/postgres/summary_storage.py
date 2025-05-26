from datetime import datetime
from sqlalchemy import select
from uuid import uuid4

from src.gears.db import DB
from ..summary_storage_models import (
    GetResult,
    CreateBody,
    CreateResult,
    UpdateBody,
)
from ..summary_storage import ErrInternal, ErrNotFound
from .models.summary import Summary


class SummaryStorage:
    def __init__(self, db: DB):
        self.db = db

    async def create(self, body: CreateBody) -> CreateResult:
        try:
            new_summary = Summary(
                id=str(uuid4()),
                file_id=body.file_id,
                content=body.content,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            async with self.db.session_maker() as session:
                session.add(new_summary)
                await session.commit()
                await session.refresh(new_summary)

                return CreateResult(id=new_summary.id)
        except Exception as e:
            raise ErrInternal(f"summary-storage: create: internal: {str(e)}")

    async def get(self, id: str) -> GetResult:
        try:
            async with self.db.session_maker() as session:
                stmt = select(Summary).where(Summary.id == id)
                result = await session.execute(stmt)
                summary = result.scalar_one_or_none()

                if summary is None:
                    raise ErrNotFound(f"summary-storage: get: not-found: id = {id}")

                return GetResult(
                    id=summary.id,
                    file_id=summary.file_id,
                    content=summary.content,
                    created_at=summary.created_at,
                    updated_at=summary.updated_at,
                )
        except ErrNotFound:
            raise
        except Exception as e:
            raise ErrInternal(f"summary-storage: get: internal: {str(e)}")

    async def get_by_file(self, file_id: str) -> GetResult:
        try:
            async with self.db.session_maker() as session:
                stmt = select(Summary).where(Summary.file_id == file_id)
                result = await session.execute(stmt)
                summary = result.scalar_one_or_none()

                if summary is None:
                    raise ErrNotFound(f"summary-storage: get_by_file: not-found: file_id = {file_id}")

                return GetResult(
                    id=summary.id,
                    file_id=summary.file_id,
                    content=summary.content,
                    created_at=summary.created_at,
                    updated_at=summary.updated_at,
                )
        except ErrNotFound:
            raise
        except Exception as e:
            raise ErrInternal(f"summary-storage: get_by_file: internal: {str(e)}")

    async def update(self, body: UpdateBody) -> GetResult:
        try:
            async with self.db.session_maker() as session:
                stmt = select(Summary).where(Summary.id == body.id)
                result = await session.execute(stmt)
                summary = result.scalar_one_or_none()

                if summary is None:
                    raise ErrNotFound(f"summary-storage: update: not-found: id = {body.id}")

                summary.content = body.content
                summary.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(summary)

                return GetResult(
                    id=summary.id,
                    file_id=summary.file_id,
                    content=summary.content,
                    created_at=summary.created_at,
                    updated_at=summary.updated_at,
                )
        except ErrNotFound:
            raise
        except Exception as e:
            raise ErrInternal(f"summary-storage: update: internal: {str(e)}")

    async def delete(self, id: str) -> bool:
        try:
            async with self.db.session_maker() as session:
                stmt = select(Summary).where(Summary.id == id)
                result = await session.execute(stmt)
                summary = result.scalar_one_or_none()

                if summary is None:
                    return False

                await session.delete(summary)
                await session.commit()
                return True
        except Exception as e:
            raise ErrInternal(f"summary-storage: delete: internal: {str(e)}") 