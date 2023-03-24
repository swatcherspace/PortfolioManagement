from datetime import datetime
import imp
import aiofiles
from config import row2dict
from fastapi import FastAPI
from typing import Optional
from database.db import Stocks
from models.stockModels import StocksModel
import requests
import pandas as pd
from controller import stock_controller
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException
from fastapi import File, UploadFile
dt = datetime.now()    # for date and time
ts = datetime.utcnow()   # for timestamp
stock = FastAPI()

@stock.post("/upload-file")
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

@stock.post("/create-fundamentals")
async def create(name: str):
    if name is None:
        return {"Message":"Please enter the name"}
    return await stock_controller.create_fundamentals(name)

@stock.post("/create-stock")
async def create(name: str):
    if name is None:
        return {"Message":"Please enter the name"}
    return await stock_controller.create_stocks(name)

@stock.delete("/delete-stock")
async def delete(name: str):
    if name is None:
        return {"Message":"Please enter the name"}
    return await stock_controller.delete_stocks(name)

@stock.get("/get-stock-by-name")
async def get_Stocks(name: str):
    if name is None:
        return {"Message":"Please enter the name"}
    return await stock_controller.get_stocks(name)

@stock.get("/get-fundamentals-by-name")
async def get_Fundamentals(name: str):
    if name is None:
        return {"Message":"Please enter the name"}
    return await stock_controller.get_fundamentals(name)

@stock.get("/get-quotes")
async def get_Quotes(name):
    return await stock_controller.get_quotes(name)

@stock.get("/get-stock-symbols")
async def get_Symbols(market_type):
    return await stock_controller.get_symbols(market_type)
