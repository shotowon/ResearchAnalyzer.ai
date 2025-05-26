from datetime import datetime
from sqlalchemy import select
from uuid import uuid4

from src.gears.db import DB
from ..message_storage_models import (
    GetResult,
    CreateBody,
    CreateResult,
    UpdateBody,
)
from ..message_storage import ErrInternal, ErrNotFound
from .models.message import Message


class MessageStorage:
    def __init__(self, db: DB):
        self.db = db

    async def create(self, body: CreateBody) -> CreateResult:
        try:
            new_message = Message(
                id=str(uuid4()),
                chat_id=body.chat_id,
                content=body.content,
                role=body.role,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            async with self.db.session_maker() as session:
                session.add(new_message)
                await session.commit()
                await session.refresh(new_message)

                return CreateResult(id=new_message.id)
        except Exception as e:
            raise ErrInternal(f"message-storage: create: internal: {str(e)}")

    async def get(self, id: str) -> GetResult:
        try:
            async with self.db.session_maker() as session:
                stmt = select(Message).where(Message.id == id)
                result = await session.execute(stmt)
                message = result.scalar_one_or_none()

                if message is None:
                    raise ErrNotFound(f"message-storage: get: not-found: id = {id}")

                return GetResult(
                    id=message.id,
                    chat_id=message.chat_id,
                    content=message.content,
                    role=message.role,
                    created_at=message.created_at,
                    updated_at=message.updated_at,
                )
        except ErrNotFound:
            raise
        except Exception as e:
            raise ErrInternal(f"message-storage: get: internal: {str(e)}")

    async def get_by_chat(self, chat_id: str) -> list[GetResult]:
        try:
            async with self.db.session_maker() as session:
                stmt = select(Message).where(Message.chat_id == chat_id)
                result = await session.execute(stmt)
                messages = result.scalars().all()

                return [
                    GetResult(
                        id=message.id,
                        chat_id=message.chat_id,
                        content=message.content,
                        role=message.role,
                        created_at=message.created_at,
                        updated_at=message.updated_at,
                    )
                    for message in messages
                ]
        except Exception as e:
            raise ErrInternal(f"message-storage: get_by_chat: internal: {str(e)}")

    async def update(self, body: UpdateBody) -> GetResult:
        try:
            async with self.db.session_maker() as session:
                stmt = select(Message).where(Message.id == body.id)
                result = await session.execute(stmt)
                message = result.scalar_one_or_none()

                if message is None:
                    raise ErrNotFound(f"message-storage: update: not-found: id = {body.id}")

                message.content = body.content
                message.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(message)

                return GetResult(
                    id=message.id,
                    chat_id=message.chat_id,
                    content=message.content,
                    role=message.role,
                    created_at=message.created_at,
                    updated_at=message.updated_at,
                )
        except ErrNotFound:
            raise
        except Exception as e:
            raise ErrInternal(f"message-storage: update: internal: {str(e)}")

    async def delete(self, id: str) -> bool:
        try:
            async with self.db.session_maker() as session:
                stmt = select(Message).where(Message.id == id)
                result = await session.execute(stmt)
                message = result.scalar_one_or_none()

                if message is None:
                    return False

                await session.delete(message)
                await session.commit()
                return True
        except Exception as e:
            raise ErrInternal(f"message-storage: delete: internal: {str(e)}") 