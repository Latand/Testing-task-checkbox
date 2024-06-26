import logging

from fastapi import APIRouter, FastAPI
from starlette.middleware.cors import CORSMiddleware

from api import routers

app = FastAPI()
prefix_router = APIRouter(prefix="/api/v1")

log_level = logging.INFO
log = logging.getLogger(__name__)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.getLogger(__name__).setLevel(logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
)


for router in [
    routers.auth_api.router,
    routers.receipts_api.router,
]:
    prefix_router.include_router(router)

app.include_router(prefix_router)
