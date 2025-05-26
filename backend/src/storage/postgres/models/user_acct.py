from typing import List
from sqlalchemy import String, Integer, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from .base import Base


class UserAcct(Base):
    __tablename__ = "user_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_activated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        index=True,
        nullable=False,
        unique=True,
    )
    username: Mapped[str] = mapped_column(String(24), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    # Relationships
    auth_tokens: Mapped[List["AuthToken"]] = relationship(back_populates="user")
    file_mappings: Mapped[List["FileMapping"]] = relationship(back_populates="user")
    ingested_files: Mapped[List["IngestedFileMapping"]] = relationship(back_populates="user")

    __table_args__ = (Index("ix_user_acct_username", "username"),)
