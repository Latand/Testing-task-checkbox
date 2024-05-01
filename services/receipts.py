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
            )
            for product in receipt_data.products
        ]

        total: Decimal = sum(product.total for product in products_response)
        rest = receipt_data.payment.amount - total
        if rest < 0:
            raise NotEnoughMoney()

        receipt = await self.repo.receipts.create_receipt(
            user_id=user_id, total=total, rest=rest, comment=receipt_data.comment
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
            comment=receipt_data.comment,
            total=total,
            rest=rest,
            created_at=receipt.created_at.strftime("%Y-%m-%d %H:%M:%S"),
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
                comment=receipt.comment,
                created_at=receipt.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            )
            for receipt in results
        ]

    async def get_receipt_by_id(self, receipt_id: int):
        receipt = await self.repo.receipts.get_receipt_by_id(receipt_id=receipt_id)
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
            comment=receipt.comment,
            rest=receipt.rest,
            user_full_name=receipt.user.full_name,
            created_at=receipt.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        )


def generate_receipt_text(receipt: CreateReceiptResponse, max_characters: int) -> str:
    block_divider = "=" * max_characters + "\n"
    items_divider = "-" * max_characters + "\n"

    text = receipt.user_full_name.center(max_characters) + "\n"
    text += block_divider

    items = [
        format_number(product.quantity)
        + " x "
        + format_number(product.price)
        + "\n"
        + format_text(product.name, max_characters, format_number(product.total))
        for product in receipt.products
    ]
    text += items_divider.join(items)
    text += block_divider

    text += format_text("СУМА:", max_characters, format_number(receipt.total))
    payment_type_text = "Готівка" if receipt.payment == PaymentType.CASH else "Картка"
    text += format_text(
        payment_type_text, max_characters, format_number(receipt.payment.amount)
    )
    text += format_text("Решта:", max_characters, format_number(receipt.rest))
    if receipt.comment:
        text += items_divider
        text += "Коментар:\n" + format_text(receipt.comment, max_characters)

    text += block_divider

    text += receipt.created_at.center(max_characters)
    text += "\n" + "Дякуємо за покупку!".center(max_characters)

    return text


def format_number(number: Decimal) -> str:
    return f"{number:,.2f}".replace(",", " ")


def format_text(
    input_text: str, max_characters: int, right_text: str | None = None
) -> str:
    words = input_text.split()
    formatted_lines = []
    current_line = ""
    right_spacing = len(right_text) + 5 if right_text else 5

    for word in words:
        # Check if the word is too long and needs truncation
        if len(word) > max_characters:
            word = word[: max_characters - right_spacing] + "..."

        # Add word to the current line if it fits
        if len(current_line) + len(word) + 1 <= max_characters:
            current_line += word + " "
        else:
            # If the word doesn't fit, finalize the current line and start a new one
            formatted_lines.append(current_line.rstrip())
            current_line = word + " "

    # Append the last line if it contains any words
    if current_line:
        formatted_lines.append(current_line.rstrip())

    if right_text:
        formatted_lines[-1] = (
            f"{formatted_lines[-1].ljust(max_characters - len(right_text))}{right_text}"
        )

    return "\n".join(formatted_lines) + "\n"
