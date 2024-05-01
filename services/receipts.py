from datetime import datetime
from decimal import Decimal
from api.exceptions import NotEnoughMoney
from api.models import (
    CreateReceiptRequest,
    CreateReceiptResponse,
    Payment,
    ProductResponse,
)
from database.models.receipts import PaymentType
from database.repo.requests import RequestsRepo


class ReceiptService:
    def __init__(self, repo: RequestsRepo) -> None:
        self.repo = repo

    async def create_receipt(self, user_id: int, receipt_data: CreateReceiptRequest):
        products_response = [
            ProductResponse(
                name=product.name,
                price=product.price,
                quantity=product.quantity,
                total=product.price * product.quantity,
                comment=product.comment,
            )
            for product in receipt_data.products
        ]

        total: Decimal = sum(product.total for product in products_response)
        rest = receipt_data.payment.amount - total
        if rest < 0:
            raise NotEnoughMoney()

        receipt = await self.repo.receipts.create_receipt(
            user_id=user_id, total=total, rest=rest
        )

        await self.repo.receipts.create_receipt_items(
            receipt_id=receipt.receipt_id, products=products_response
        )
        await self.repo.payments.create_payment(
            receipt_id=receipt.receipt_id,
            payment_type=receipt_data.payment.type,
            amount=receipt_data.payment.amount,
        )
        await self.repo.session.commit()

        return CreateReceiptResponse(
            receipt_id=receipt.receipt_id,
            products=products_response,
            payment=receipt_data.payment,
            total=total,
            rest=rest,
            created_at=receipt.created_at.strftime("%Y-%m-%d %H:%M:%S %Z"),
        )

    async def get_receipts(
        self,
        user_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        min_total: Decimal | None = None,
        max_total: Decimal | None = None,
        payment_type: PaymentType | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[CreateReceiptResponse]:
        results = await self.repo.receipts.get_receipts(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            min_total=min_total,
            max_total=max_total,
            payment_type=payment_type,
            limit=limit,
            offset=offset,
        )
        return [
            CreateReceiptResponse(
                receipt_id=receipt.receipt_id,
                products=[
                    ProductResponse(
                        name=item.product_name,
                        price=item.price_per_unit,
                        quantity=item.quantity,
                        total=item.total_price,
                    )
                    for item in receipt.items
                ],
                payment=Payment(
                    type=receipt.payment.type,
                    amount=receipt.payment.amount,
                ),
                total=receipt.total,
                rest=receipt.rest,
                created_at=receipt.created_at.strftime("%Y-%m-%d %H:%M:%S %Z"),
            )
            for receipt in results
        ]

    async def get_receipt_by_id(self, user_id: int, receipt_id: int):
        receipt = await self.repo.receipts.get_receipt_by_id(
            user_id=user_id, receipt_id=receipt_id
        )
        if not receipt:
            return None

        return CreateReceiptResponse(
            receipt_id=receipt.receipt_id,
            products=[
                ProductResponse(
                    name=item.product_name,
                    price=item.price_per_unit,
                    quantity=item.quantity,
                    total=item.total_price,
                )
                for item in receipt.items
            ],
            payment=Payment(
                type=receipt.payment.type,
                amount=receipt.payment.amount,
            ),
            total=receipt.total,
            rest=receipt.rest,
            created_at=receipt.created_at.strftime("%Y-%m-%d %H:%M:%S %Z"),
        )
