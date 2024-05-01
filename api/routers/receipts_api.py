from datetime import datetime
from decimal import Decimal
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response

from api.dependencies import get_repository
from api.exceptions import NotEnoughMoney
from database.models.receipts import PaymentType
from database.repo.requests import RequestsRepo
from services.auth import get_current_user


from api.models import CreateReceiptRequest, CreateReceiptResponse
from database.models import User
from services.receipts import ReceiptService, generate_receipt_text

router = APIRouter(prefix="/receipts")


@router.post(
    "/",
    response_model=CreateReceiptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_receipt(
    receipt_request: CreateReceiptRequest,
    user: Annotated[User, Depends(get_current_user)],
    repo: Annotated[RequestsRepo, Depends(get_repository)],
):
    receipt_service = ReceiptService(repo)
    try:
        response = await receipt_service.create_receipt(user.user_id, receipt_request)
    except NotEnoughMoney:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough money"
        )

    return response


@router.get("/", response_model=list[CreateReceiptResponse])
async def get_receipts(
    user: Annotated[User, Depends(get_current_user)],
    repo: Annotated[RequestsRepo, Depends(get_repository)],
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    min_total: Decimal | None = None,
    max_total: Decimal | None = None,
    payment_type: PaymentType | None = None,
    limit: int = Query(10, gt=0),
    offset: int = Query(0, ge=0),
):
    receipt_service = ReceiptService(repo)
    result = await receipt_service.get_receipts(
        user_id=user.user_id,
        start_date=start_date,
        end_date=end_date,
        min_total=min_total,
        max_total=max_total,
        payment_type=payment_type,
        offset=offset,
        limit=limit,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Receipts not found"
        )

    return result


@router.get("/{receipt_id}", response_model=CreateReceiptResponse)
async def get_receipt_by_id(
    receipt_id: int,
    repo: Annotated[RequestsRepo, Depends(get_repository)],
):
    receipt_service = ReceiptService(repo)
    result = await receipt_service.get_receipt_by_id(receipt_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found"
        )

    return result


@router.get("/show/{receipt_id}/")
async def show_receipt_by_id(
    receipt_id: int,
    repo: Annotated[RequestsRepo, Depends(get_repository)],
    max_characters: int = Query(30, ge=20),
):
    receipt_service = ReceiptService(repo)
    result = await receipt_service.get_receipt_by_id(receipt_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found"
        )

    receipt_text = generate_receipt_text(result, max_characters)

    return Response(content=receipt_text, media_type="text/plain")
