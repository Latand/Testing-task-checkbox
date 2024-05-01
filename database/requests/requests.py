from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from database.requests.receipts import ReceiptRepo
from database.requests.users import UserRepo


@dataclass
class RequestsRepo:
    session: AsyncSession

    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)

    @property
    def receipts(self) -> ReceiptRepo:
        return ReceiptRepo(self.session)
