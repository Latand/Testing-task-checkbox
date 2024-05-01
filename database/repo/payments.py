from decimal import Decimal

from sqlalchemy import insert

from database.models.receipts import Payment, PaymentType
from database.repo.base import BaseRepo


class PaymentsRepo(BaseRepo):
    async def create_payment(
        self, receipt_id: int, payment_type: PaymentType, amount: Decimal
    ):
        await self.session.execute(
            insert(Payment).values(
                receipt_id=receipt_id, type=payment_type, amount=amount
            )
        )
