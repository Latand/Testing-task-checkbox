from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_repository
from api.exceptions import NotEnoughMoney
from database.requests.requests import RequestsRepo
from services.auth import get_current_user


from api.models import CreateReceiptRequest, CreateReceiptResponse
from database.models import User
from services.receipts import ReceiptService

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
    receipt_service = ReceiptService(repo)
    try:
        response = await receipt_service.create_receipt(user.user_id, receipt_request)
    except NotEnoughMoney:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough money"
        )

    return response
