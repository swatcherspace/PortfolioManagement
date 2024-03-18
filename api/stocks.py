from datetime import datetime
import aiofiles
from fastapi import FastAPI
from controller import stock_controller
from fastapi import Depends, FastAPI, HTTPException
from fastapi import File, UploadFile
dt = datetime.now()    # for date and time
ts = datetime.utcnow()   # for timestamp
stock = FastAPI()

# Create some routes:

# @stock.get("/my-route")
# async def get_tasks():
#     # We can modify/read the Rocketry's runtime session
#     return session.tasks

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
async def create(name: str, market_type: str):
    if name is None:
        return {"Message":"Please enter the name"}
    return await stock_controller.create_stocks(name, market_type)

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
