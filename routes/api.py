"""
Author: Ratnam, Abhi
Purpose: Invokes Routes
Modified Date: 31st Jan 2023 
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.stocks import stock


app = FastAPI()

"""Add arguments to the middleware"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=stock.router)