from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from .base import Base
from .user_acct import UserAcct
from .file_mapping import FileMapping


class IngestedFileMapping(Base):
    __tablename__ = "ingested_file_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_accounts.id"))
    user = relationship(UserAcct, backref=backref("auth_tokens", uselist=False))
    file_mapping_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("file_mappings.id")
    )
    file_mapping = relationship(FileMapping, backref=backref("ingested", uselist=False))
    document_id: Mapped[str] = mapped_column(String(), nullable=False)
