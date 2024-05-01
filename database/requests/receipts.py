from api.models import CreateReceiptRequest
from database.requests.base import BaseRepo


class ReceiptRepo(BaseRepo):
    async def create_receipt(self, user_id: int, receipt_data: CreateReceiptRequest):
        pass
