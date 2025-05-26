from typing import List
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .user_acct import UserAcct
from .file_mapping import FileMapping


class IngestedFileMapping(Base):
    __tablename__ = "ingested_file_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_accounts.id"))
    file_mapping_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("file_mappings.id")
    )
    document_id: Mapped[str] = mapped_column(String(), nullable=False)

    # Relationships
    user: Mapped["UserAcct"] = relationship(back_populates="ingested_files")
    file_mapping: Mapped["FileMapping"] = relationship(back_populates="ingested")
    summaries: Mapped[List["Summary"]] = relationship(back_populates="file")
    chats: Mapped[List["Chat"]] = relationship(back_populates="file")
