from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from .base import Base
from .user_acct import UserAcct


class FileMapping(Base):
    __tablename__ = "file_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_accounts.id"))
    filename: Mapped[str] = mapped_column(String(), nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        default="binary/octet-stream",
    )

    # Relationships
    user: Mapped["UserAcct"] = relationship(back_populates="file_mappings")
    ingested: Mapped["IngestedFileMapping"] = relationship(back_populates="file_mapping")
