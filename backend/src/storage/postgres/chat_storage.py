from datetime import datetime
from sqlalchemy import select
from uuid import uuid4

from src.gears.db import DB
from ..chat_storage_models import (
    GetResult,
    CreateBody,
    CreateResult,
    UpdateBody,
)
from ..chat_storage import ErrInternal, ErrNotFound
from .models.chat import Chat


class ChatStorage:
    def __init__(self, db: DB):
        self.db = db

    async def create(self, body: CreateBody) -> CreateResult:
        try:
            new_chat = Chat(
                id=str(uuid4()),
                file_id=body.file_id,
                title=body.title,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            async with self.db.session_maker() as session:
                session.add(new_chat)
                await session.commit()
                await session.refresh(new_chat)

                return CreateResult(id=new_chat.id)
        except Exception as e:
            raise ErrInternal(f"chat-storage: create: internal: {str(e)}")

    async def get(self, id: str) -> GetResult:
        try:
            async with self.db.session_maker() as session:
                stmt = select(Chat).where(Chat.id == id)
                result = await session.execute(stmt)
                chat = result.scalar_one_or_none()

                if chat is None:
                    raise ErrNotFound(f"chat-storage: get: not-found: id = {id}")

                return GetResult(
                    id=chat.id,
                    file_id=chat.file_id,
                    title=chat.title,
                    created_at=chat.created_at,
                    updated_at=chat.updated_at,
                )
        except ErrNotFound:
            raise
        except Exception as e:
            raise ErrInternal(f"chat-storage: get: internal: {str(e)}")

    async def get_by_file(self, file_id: str) -> list[GetResult]:
        try:
            async with self.db.session_maker() as session:
                stmt = select(Chat).where(Chat.file_id == file_id)
                result = await session.execute(stmt)
                chats = result.scalars().all()

                return [
                    GetResult(
                        id=chat.id,
                        file_id=chat.file_id,
                        title=chat.title,
                        created_at=chat.created_at,
                        updated_at=chat.updated_at,
                    )
                    for chat in chats
                ]
        except Exception as e:
            raise ErrInternal(f"chat-storage: get_by_file: internal: {str(e)}")

    async def update(self, body: UpdateBody) -> GetResult:
        try:
            async with self.db.session_maker() as session:
                stmt = select(Chat).where(Chat.id == body.id)
                result = await session.execute(stmt)
                chat = result.scalar_one_or_none()

                if chat is None:
                    raise ErrNotFound(f"chat-storage: update: not-found: id = {body.id}")

                chat.title = body.title
                chat.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(chat)

                return GetResult(
                    id=chat.id,
                    file_id=chat.file_id,
                    title=chat.title,
                    created_at=chat.created_at,
                    updated_at=chat.updated_at,
                )
        except ErrNotFound:
            raise
        except Exception as e:
            raise ErrInternal(f"chat-storage: update: internal: {str(e)}")

    async def delete(self, id: str) -> bool:
        try:
            async with self.db.session_maker() as session:
                stmt = select(Chat).where(Chat.id == id)
                result = await session.execute(stmt)
                chat = result.scalar_one_or_none()

                if chat is None:
                    return False

                await session.delete(chat)
                await session.commit()
                return True
        except Exception as e:
            raise ErrInternal(f"chat-storage: delete: internal: {str(e)}") 