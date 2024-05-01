from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from database.repo.payments import PaymentsRepo
from database.repo.receipts import ReceiptRepo
from database.repo.users import UserRepo


@dataclass
class RequestsRepo:
    session: AsyncSession

    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)

    @property
    def receipts(self) -> ReceiptRepo:
        return ReceiptRepo(self.session)

    @property
    def payments(self) -> PaymentsRepo:
        return PaymentsRepo(self.session)
