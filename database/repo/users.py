from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from database.models import User
from database.repo.base import BaseRepo


class UserRepo(BaseRepo):
    async def create_user(
        self,
        full_name: str,
        username: str,
        password_hash: str,
    ):
        insert_stmt = (
            insert(User)
            .values(username=username, full_name=full_name, password_hash=password_hash)
            .on_conflict_do_nothing()
            .returning(User)
        )
        await self.session.execute(insert_stmt)

    async def get_user(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )

        return result.scalar_one_or_none()
