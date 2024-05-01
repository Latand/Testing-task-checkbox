from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, TableNameMixin, TimestampMixin, int_pk


class PaymentType(Enum):
    CASH = "cash"
    CARD = "card"


class Receipt(Base, TableNameMixin, TimestampMixin):
    receipt_id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE")
    )
    total: Mapped[Decimal] = mapped_column(DECIMAL(16, 4))
    rest: Mapped[Decimal] = mapped_column(DECIMAL(16, 4))
    comment: Mapped[Optional[str]]

    items: Mapped[list["ReceiptItem"]] = relationship(
        "ReceiptItem", back_populates="receipt"
    )
    payment: Mapped["Payment"] = relationship("Payment", back_populates="receipt")
    user: Mapped["User"] = relationship("User", back_populates="receipts")


class ReceiptItem(Base, TableNameMixin):
    item_id: Mapped[int_pk]
    receipt_id: Mapped[int] = mapped_column(
        ForeignKey("receipts.receipt_id", ondelete="CASCADE")
    )

    product_name: Mapped[str] = mapped_column(String(255))
    price_per_unit: Mapped[Decimal] = mapped_column(DECIMAL(16, 4))
    quantity: Mapped[Decimal] = mapped_column(DECIMAL(10, 4))
    total_price: Mapped[Decimal] = mapped_column(DECIMAL(16, 4))

    receipt: Mapped["Receipt"] = relationship("Receipt", back_populates="items")


class Payment(Base, TableNameMixin, TimestampMixin):
    payment_id: Mapped[int_pk]
    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipts.receipt_id"))

    type: Mapped[PaymentType]
    amount: Mapped[Decimal] = mapped_column(DECIMAL(16, 4))

    receipt: Mapped["Receipt"] = relationship("Receipt", back_populates="payment")
