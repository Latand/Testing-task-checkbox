from typing import Optional
from sqlalchemy.orm import Mapped
from sqlalchemy import BIGINT, String
from sqlalchemy.orm import mapped_column

from database.models.base import Base, TableNameMixin, TimestampMixin


class User(Base, TableNameMixin, TimestampMixin):
    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(64), unique=True)

    password_hash: Mapped[str] = String(255)
