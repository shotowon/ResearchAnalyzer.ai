from datetime import datetime
from typing import List
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .ingested_file_mapping import IngestedFileMapping


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_id: Mapped[int] = mapped_column(Integer, ForeignKey("ingested_file_mappings.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    file: Mapped["IngestedFileMapping"] = relationship(back_populates="chats")
    messages: Mapped[List["Message"]] = relationship(back_populates="chat", cascade="all, delete-orphan") 