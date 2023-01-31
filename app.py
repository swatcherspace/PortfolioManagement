"""
Author: Ratnam, Abhi
Purpose: Invokes routes
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.api import router as api_router


app = FastAPI()

"""Add arguments to the middleware"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""Adding router endpoints"""
app.include_router(api_router)