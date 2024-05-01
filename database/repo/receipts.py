from decimal import Decimal

from sqlalchemy import insert, select
from sqlalchemy.orm import selectinload
from api.models import ProductResponse
from database.models.receipts import PaymentType, Receipt, ReceiptItem, Payment
from database.repo.base import BaseRepo


class ReceiptRepo(BaseRepo):
    async def create_receipt(self, user_id: int, total: Decimal, rest: Decimal):
        result = await self.session.execute(
            insert(Receipt)
            .values(user_id=user_id, total=total, rest=rest)
            .returning(Receipt)
        )
        return result.scalar_one()

    async def create_receipt_items(
        self, receipt_id: int, products: list[ProductResponse]
    ):
        await self.session.execute(
            insert(ReceiptItem).values(
                [
                    dict(
                        receipt_id=receipt_id,
                        product_name=product.name,
                        price_per_unit=product.price,
                        quantity=product.quantity,
                        total_price=product.total,
                        comment=product.comment,
                    )
                    for product in products
                ]
            )
        )

    async def get_receipts(
        self,
        user_id: int,
        start_date: str | None = None,
        end_date: str | None = None,
        min_total: Decimal | None = None,
        max_total: Decimal | None = None,
        payment_type: PaymentType | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ):
        select_stmt = (
            select(Receipt)
            .options(selectinload(Receipt.payment))
            .options(selectinload(Receipt.items))
            .where(
                Receipt.user_id == user_id,
            )
        )

        if start_date:
            select_stmt = select_stmt.where(Receipt.created_at >= start_date)

        if end_date:
            select_stmt = select_stmt.where(Receipt.created_at <= end_date)

        if min_total:
            select_stmt = select_stmt.where(Receipt.total >= min_total)

        if max_total:
            select_stmt = select_stmt.where(Receipt.total <= max_total)

        if payment_type:
            select_stmt = select_stmt.join(Payment).where(Payment.type == payment_type)

        if limit:
            select_stmt = select_stmt.limit(limit)

        if offset:
            select_stmt = select_stmt.offset(offset)

        result = await self.session.scalars(select_stmt)

        return result.all()

    async def get_receipt_by_id(self, user_id: int, receipt_id: int):
        result = await self.session.execute(
            select(Receipt)
            .options(selectinload(Receipt.payment))
            .options(selectinload(Receipt.items))
            .where(
                Receipt.user_id == user_id,
                Receipt.receipt_id == receipt_id,
            )
        )
        return result.scalar_one_or_none()