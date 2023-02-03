"""
Author: Ratnam, Abhi
Purpose: Invokes Routes
Modified Date: 31st Jan 2023 
"""
from fastapi import APIRouter
from api.stocks import stock

router = APIRouter()


"""Add stock API router"""
router.include_router(router=stock.router)