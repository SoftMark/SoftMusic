import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import main_router

app = FastAPI()
app.include_router(main_router)

origins = [
    "http://localhost:63036",  # Angular
    "http://127.0.0.1:63036",
    "http://127.0.0.1:4200",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,                      # Список разрешенных источников
    allow_credentials=True,                     # Разрешить куки и заголовки авторизации
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], # Разрешенные HTTP-методы
    allow_headers=["*"],                        # Разрешить все заголовки
)

DEBUG = True  # TODO: load from env


# TODO: Use "uvicorn src.run:app --reload"
if DEBUG and __name__ == '__main__':
    uvicorn.run('run:app', reload=True)
