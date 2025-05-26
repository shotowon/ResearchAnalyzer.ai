from datetime import datetime
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey("chats.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)  # e.g., 'user', 'assistant'
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )

    # Relationships
    chat: Mapped["Chat"] = relationship(back_populates="messages") 