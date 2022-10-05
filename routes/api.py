from fastapi import APIRouter
from api.stocks import stock

router = APIRouter()
router.include_router(stock.router)

