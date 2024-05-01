from pydantic import BaseModel, condecimal

from database.models.receipts import PaymentType


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class Product(BaseModel):
    name: str
    price: condecimal(gt=0, max_digits=16, decimal_places=2)  # type: ignore
    quantity: condecimal(gt=0, max_digits=10, decimal_places=3)  # type: ignore


class Payment(BaseModel):
    type: PaymentType
    amount: condecimal(gt=0, max_digits=16, decimal_places=2)  # type: ignore


class CreateReceiptRequest(BaseModel):
    products: list[Product]
    payment: Payment
    comment: str | None = None


class ProductResponse(Product):
    total: condecimal(gt=0, max_digits=16, decimal_places=2)  # type: ignore


class CreateReceiptResponse(BaseModel):
    receipt_id: int
    products: list[ProductResponse]
    payment: Payment
    comment: str | None = None
    total: condecimal(gt=0, max_digits=16, decimal_places=2)  # type: ignore
    rest: condecimal(ge=0, max_digits=16, decimal_places=2)  # type: ignore
    created_at: str


class SignupRequest(BaseModel):
    username: str
    full_name: str
    password: str


class GetTokenRequest(BaseModel):
    username: str
    password: str
