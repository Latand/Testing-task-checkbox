from decimal import Decimal

from sqlalchemy import insert
from api.models import ProductResponse
from database.models.receipts import Receipt, ReceiptItem
from database.requests.base import BaseRepo


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
