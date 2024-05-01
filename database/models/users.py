from sqlalchemy import BIGINT, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, TableNameMixin, TimestampMixin


class User(Base, TableNameMixin, TimestampMixin):
    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(64), unique=True)

    password_hash: Mapped[str] = mapped_column(String(255))

    receipts: Mapped[list["Receipt"]] = relationship("Receipt", back_populates="user")
