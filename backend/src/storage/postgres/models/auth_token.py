from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from .base import Base
from .user_acct import UserAcct


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_accounts.id"))
    user = relationship(UserAcct, backref=backref("auth_tokens", uselist=False))
    token: Mapped[str] = mapped_column(String(), nullable=False)
