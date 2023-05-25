from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from routes.api import router as api_router
import uvicorn
from fastapi import FastAPI
import os
import random
import time
import asyncio
import uvicorn
from scheduler import app as app_rocketry
import logging

app = FastAPI()

origins = ["*"]

app.add_middleware(
                        CORSMiddleware,
                        allow_origins=origins,
                        allow_credentials=True,
                        allow_methods=["*"],
                        allow_headers=["*"],)

app.include_router(api_router)

class Server(uvicorn.Server):
    """Customized uvicorn.Server

    Uvicorn server overrides signals and we need to include
    Rocketry to the signals."""
    def handle_exit(self, sig: int, frame) -> None:
        app_rocketry.session.shut_down()
        return super().handle_exit(sig, frame)


async def main():
    "Run scheduler and the API"
    server = Server(config=uvicorn.Config(app, workers=1, loop="asyncio"))

    api = asyncio.create_task(server.serve())
    sched = asyncio.create_task(app_rocketry.serve())

    await asyncio.wait([sched, api])

if __name__ == "__main__":
    logger = logging.getLogger("rocketry.task")
    logger.addHandler(logging.StreamHandler())
    asyncio.run(main())
    