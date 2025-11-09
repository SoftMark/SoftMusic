from fastapi import APIRouter

from src.api.books import router as books_router
from src.api.tracks import router as tracks_router

main_router = APIRouter()

main_router.include_router(books_router)
main_router.include_router(tracks_router)
