from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .user_acct import UserAcct


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_accounts.id"))
    token: Mapped[str] = mapped_column(String(), nullable=False, index=True)

    # Relationships
    user: Mapped["UserAcct"] = relationship(back_populates="auth_tokens")
