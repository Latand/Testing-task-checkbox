from decimal import Decimal
from api.exceptions import NotEnoughMoney
from api.models import CreateReceiptRequest, CreateReceiptResponse, ProductResponse
from database.requests.requests import RequestsRepo


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
        await self.repo.session.commit()

        return CreateReceiptResponse(
            receipt_id=receipt.receipt_id,
            products=products_response,
            payment=receipt_data.payment,
            total=total,
            rest=rest,
            created_at=receipt.created_at.strftime("%Y-%m-%d %H:%M:%S %Z"),
        )
