from fastapi import APIRouter, Depends, status

from api.dependencies import get_repository
from database.requests.requests import RequestsRepo
from services.auth import get_current_user


from api.models import CreateReceiptRequest, CreateReceiptResponse
from database.models import User

router = APIRouter()


@router.post(
    "/receipts",
    response_model=CreateReceiptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_receipt(
    receipt_request: CreateReceiptRequest,
    user: User = Depends(get_current_user),
    repo: RequestsRepo = Depends(get_repository),
):
    receipt = await repo.receipts.create_receipt(
        user_id=user.user_id, receipt_data=receipt_request
    )

    return receipt
