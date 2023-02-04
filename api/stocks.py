"""
Author: Ratnam, Abhi
Date: 4th Feb, 2023
Purpose: Creates portfolio routes
"""
from datetime import datetime
import aiofiles
from fastapi import APIRouter
from controller import stock_controller
from controller.stock_controller import Stock
from fastapi import Depends, FastAPI, HTTPException
from fastapi import File, UploadFile
dt = datetime.now()    # for date and time
ts = datetime.utcnow()   # for timestamp

route = APIRouter()
stock = Stock()


@route.post("/upload-file")
async def upload_file(name: str, file: UploadFile = File(...)):
    try:
        contents = await file.read()
        async with aiofiles.open(file.filename, 'wb') as f:
            await f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        await file.close()
    return await stock_controller.upload_file(name, contents)


@route.post("/create-fundamentals")
async def create_fundamentals(name: str):
    """
    Route to create stock fundamentals

    :argument: name [str]

    :returns: dict
    """
    if name is None:
        return {"Message":"Please enter the name"}

    return await stock.create_fundamentals(name)


@route.post("/create-stock")
async def create_stock(name: str):
    if name is None:
        return {"Message":"Please enter the name"}
    return await stock_controller.create_stocks(name)

@route.delete("/delete-stock")
async def delete(name: str):
    if name is None:
        return {"Message":"Please enter the name"}
    return await stock_controller.delete_stocks(name)

@route.get("/get-stock-by-name")
async def get_Stocks(name: str):
    if name is None:
        return {"Message":"Please enter the name"}
    return await stock_controller.get_stocks(name)

@route.get("/get-fundamentals-by-name")
async def get_Fundamentals(name: str):
    if name is None:
        return {"Message":"Please enter the name"}
    return await stock_controller.get_fundamentals(name)

@route.get("/get-quotes")
async def get_Quotes(name):
    return await stock_controller.get_quotes(name)

@route.get("/get-stock-symbols")
async def get_Symbols():
    return await stock_controller.get_symbols()
