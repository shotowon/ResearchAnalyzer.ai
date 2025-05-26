from typing import List
from sqlalchemy import select

from src.gears.db import DB
from ..file_mapping_storage_models import (
    GetResult,
    CreateBody,
    CreateResult,
    CreateIngestedResult,
    CreateIngestedBody,
    GetIngestedResult,
)
from ..file_mapping_storage import ErrInternal, ErrNotFound
from .models.file_mapping import FileMapping
from .models.ingested_file_mapping import IngestedFileMapping


class MappingStorage:
    def __init__(self, db: DB):
        self.db = db

    async def list(
        self, user_id: int, limit: int = 15, offset: int = 0
    ) -> List[GetResult]:
        try:
            async with self.db.session_maker() as session:
                stmt = (
                    select(FileMapping)
                    .where(FileMapping.user_id == user_id)
                    .offset(offset=offset)
                    .limit(limit=limit)
                )

                result = await session.execute(stmt)
                records = result.scalars().all()
                file_mappings = [
                    GetResult(
                        id=record.id,
                        user_id=record.user_id,
                        filename=record.filename,
                        content_type=record.content_type,
                    )
                    for record in records
                ]

                return file_mappings
        except Exception as e:
            raise ErrInternal("file-mapping-storage: list: internal: {}".format(str(e)))

    async def get(self, id: int) -> GetResult:
        try:
            async with self.db.session_maker() as session:
                stmt = select(FileMapping).where(FileMapping.id == id)

                result = await session.execute(stmt)
                mapping = result.scalar_one_or_none()
        except Exception as e:
            raise ErrInternal("file-mapping-storage: get: internal: {}".format(str(e)))

        if mapping is None:
            raise ErrNotFound(
                "file-mapping-storage: get: not-found: id = {}".format(id)
            )

        return GetResult(
            id=mapping.id,
            user_id=mapping.user_id,
            filename=mapping.filename,
            content_type=mapping.content_type,
        )

    async def create(self, body: CreateBody) -> CreateResult:
        try:
            new_mapping = FileMapping(
                user_id=body.user_id,
                filename=body.filename,
                content_type=body.content_type,
            )

            async with self.db.session_maker() as session:
                session.add(new_mapping)
                await session.commit()
                await session.refresh(new_mapping)

                return CreateResult(id=new_mapping.id)
        except Exception as e:
            raise ErrInternal(
                "file-mapping-storage: create: internal: {}".format(str(e))
            )

    async def list_ingested(
        self, user_id: int, limit: int = 15, offset: int = 0
    ) -> List[GetIngestedResult]:
        try:
            async with self.db.session_maker() as session:
                stmt = (
                    select(IngestedFileMapping)
                    .where(IngestedFileMapping.user_id == user_id)
                    .offset(offset=offset)
                    .limit(limit=limit)
                )

                result = await session.execute(stmt)
                records = result.scalars().all()
                file_mappings = [
                    GetIngestedResult(
                        id=record.id,
                        user_id=record.user_id,
                        mapping_id=record.file_mapping_id,
                        document_id=record.document_id,
                    )
                    for record in records
                ]

                return file_mappings
        except Exception as e:
            raise ErrInternal(
                "file-mapping-storage: list_ingested: internal: {}".format(str(e))
            )

    async def get_ingested(self, id: int) -> GetIngestedResult:
        try:
            async with self.db.session_maker() as session:
                stmt = select(IngestedFileMapping).where(IngestedFileMapping.id == id)

                result = await session.execute(stmt)
                mapping = result.scalar_one_or_none()
        except Exception as e:
            raise ErrInternal(
                "file-mapping-storage: get_ingested: internal: {}".format(str(e))
            )

        if mapping is None:
            raise ErrNotFound(
                "file-mapping-storage: get_ingested: not-found: id = {}".format(id)
            )

        return GetIngestedResult(
            id=mapping.id,
            user_id=mapping.user_id,
            mapping_id=mapping.file_mapping_id,
            document_id=mapping.document_id,
        )

    async def create_ingested(self, body: CreateIngestedBody) -> CreateIngestedResult:
        try:
            new_mapping = IngestedFileMapping(
                user_id=body.user_id,
                file_mapping_id=body.mapping_id,
                document_id=body.document_id,
            )

            async with self.db.session_maker() as session:
                session.add(new_mapping)
                await session.commit()
                await session.refresh(new_mapping)

                return CreateIngestedResult(id=new_mapping.id)
        except Exception as e:
            raise ErrInternal(
                "file-mapping-storage: create: internal: {}".format(str(e))
            )
