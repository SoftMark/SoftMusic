import uvicorn
from fastapi import FastAPI

from src.api import main_router

app = FastAPI()
app.include_router(main_router)

DEBUG = True  # TODO: load from env


# TODO: Use "uvicorn src.run:app --reload"
if DEBUG and __name__ == '__main__':
    uvicorn.run('run:app', reload=True)
